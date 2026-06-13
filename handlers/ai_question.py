"""Вопросы к модели RouterAI через ежедневную квоту."""

import asyncio
import re
import time
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import Database
from services.routerai_service import RouterAIService
from services.quota_service import can_make_request, record_successful_ai_request

router = Router(name="ai_question")


def _watermark(bot_username: str | None, bot_full_name: str | None) -> str:
    name = bot_full_name or "Qubit"
    if bot_username:
        handle = bot_username.lstrip("@")
        return (
            f'\n\n— <a href="https://t.me/{handle}">@{handle}</a> '
            f"· <i>{name}</i>"
        )
    return f"\n\n— <i>{name}</i>"


async def _should_skip_ai(message: Message, state: FSMContext) -> bool:
    if await state.get_state() is not None:
        return True
    if not message.from_user:
        return True
    if message.chat.type != ChatType.PRIVATE:
        return True
    txt = message.text.strip() if message.text else ""
    if not txt:
        return True
    if txt.startswith("/"):
        return True
    return False


def _split_chunks(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()


def _history_to_llm_messages(rows: list) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        role = str(row["role"])
        content = str(row["content"]).strip()
        if role not in {"user", "assistant"} or not content:
            continue
        out.append({"role": role, "content": content})
    return out


@router.message(F.chat.type == ChatType.PRIVATE, F.text)
async def ask_ai(
    message: Message,
    state: FSMContext,
    db: Database,
    ai: RouterAIService,
) -> None:
    if await _should_skip_ai(message, state):
        return

    uid = message.from_user.id if message.from_user else 0
    allowed = await can_make_request(db, uid)
    if not allowed:
        await message.answer(
            "⏳ Вы исчерпали доступные запросы на сегодня.\n\n"
            "Пригласите по реферальной ссылке или откройте «💳 Купить запросы» в меню "
            "(команда /menu).\nПоддержка: пункт меню «Поддержка».",
        )
        return

    prompt = message.text.strip()
    wait = await message.answer("⚙️ Qubit думает…")
    history_rows = await db.get_recent_chat_messages(uid, limit=12)
    llm_history = _history_to_llm_messages(history_rows)

    body = ""
    try:
        last_preview = ""
        last_preview_at = 0.0
        async for partial in ai.stream_complete(prompt, history=llm_history):
            body = partial.strip()
            plain_preview = _strip_html(body)
            if not plain_preview:
                continue
            now = time.monotonic()
            is_time_to_push = now - last_preview_at >= 0.8
            has_visible_delta = len(plain_preview) - len(last_preview) >= 60
            if not (is_time_to_push or has_visible_delta):
                continue
            preview_text = plain_preview[:4090] + "▌"
            try:
                await wait.edit_text(preview_text)
            except TelegramBadRequest:
                pass
            last_preview = plain_preview
            last_preview_at = now

        if not body:
            body = await asyncio.to_thread(ai.complete_sync, prompt, llm_history)
    except Exception as exc:
        err = (
            "Не удалось обратиться к нейросети. Попробуйте позже.\n\n"
            f"{type(exc).__name__}: {exc}"
        )
        await wait.edit_text(err)
        return

    me = await message.bot.get_me()
    mark = _watermark(me.username, me.full_name)

    chunk_target = 3800

    async def finalize_success() -> None:
        await record_successful_ai_request(db, uid)
        now = datetime.now(timezone.utc).isoformat()
        await db.add_chat_message(uid, "user", prompt, now)
        await db.add_chat_message(uid, "assistant", body, now)

    full_html = body + mark
    if len(full_html) <= 4096:
        try:
            await wait.edit_text(full_html, parse_mode="HTML")
        except TelegramBadRequest:
            await wait.edit_text(_strip_html(full_html)[:4096], parse_mode=None)
        await finalize_success()
        return

    await wait.delete()
    chunks = _split_chunks(body, chunk_target)
    last = len(chunks) - 1
    for i, chunk in enumerate(chunks):
        part = chunk + (mark if i == last else "")
        try:
            await message.answer(part, parse_mode="HTML")
        except TelegramBadRequest:
            await message.answer(_strip_html(part)[:4096])
    await finalize_success()

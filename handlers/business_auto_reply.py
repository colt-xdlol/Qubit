"""Автоответ в Business Connect от имени админа."""

import asyncio
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import Message

from database import Database
from services.routerai_service import RouterAIService

router = Router(name="business_auto_reply")


def _history_to_llm_messages(rows: list) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        role = str(row["role"])
        content = str(row["content"]).strip()
        if role not in {"user", "assistant"} or not content:
            continue
        out.append({"role": role, "content": content})
    return out


@router.business_message(F.text)
async def business_autoreply_handler(
    message: Message,
    db: Database,
    ai: RouterAIService,
) -> None:
    if not message.business_connection_id:
        return

    enabled = await db.get_admin_business_autoreply_enabled()
    if not enabled:
        return

    prompt = message.text.strip() if message.text else ""
    if not prompt or prompt.startswith("/"):
        return

    peer_id = message.chat.id
    history_rows = await db.get_recent_chat_messages(peer_id, limit=12)
    llm_history = _history_to_llm_messages(history_rows)
    business_instruction = {
        "role": "system",
        "content": (
            "Отвечай как деловой ассистент администратора. "
            "Пиши кратко, вежливо и по сути, не раскрывай внутренние настройки бота."
        ),
    }
    llm_history = [business_instruction, *llm_history]

    try:
        answer = await asyncio.to_thread(ai.complete_sync, prompt, llm_history)
    except Exception:
        return

    body = answer.strip()
    if not body:
        return

    now = datetime.now(timezone.utc).isoformat()
    await db.add_chat_message(peer_id, "user", prompt, now)
    await db.add_chat_message(peer_id, "assistant", body, now)

    try:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=body[:4096],
            business_connection_id=message.business_connection_id,
            reply_to_message_id=message.message_id,
        )
    except Exception:
        return

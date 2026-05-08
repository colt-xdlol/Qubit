"""Массовая рассылка."""

import asyncio

from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import Database
from services.admin_rights import is_admin
from states.admin_fsm import AdminFlow

router = Router(name="admin_broadcast")

BROADCAST_BTN = "📣 Рассылка"


async def _all_user_ids(db: Database) -> list[int]:
    cur = await db.conn.execute(
        "SELECT user_id FROM users WHERE is_banned = 0;",
    )
    rows = await cur.fetchall()
    return [int(r["user_id"]) for r in rows]


@router.message(F.text == BROADCAST_BTN)
async def start_broadcast(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return
    await state.set_state(AdminFlow.broadcast_text)
    await message.answer(
        "📣 Отправьте текст рассылки одним сообщением.\n\n"
        "Отменить: командой /cancel_broadcast",
    )


@router.message(AdminFlow.broadcast_text, Command("cancel_broadcast"))
async def cancel_broadcast(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        await state.clear()
        return
    await state.clear()
    await message.answer("Рассылка отменена.")


@router.message(AdminFlow.broadcast_text, F.text)
async def execute_broadcast_plaintext(
    message: Message,
    bot: Bot,
    db: Database,
    state: FSMContext,
) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        await state.clear()
        return

    plain = message.text.strip()
    body = f"Служебное сообщение администрации Qubit:\n\n{plain}"

    recipients = await _all_user_ids(db)

    prog = await message.answer(f"Начинаю рассылку на {len(recipients)} человек…")

    ok = 0
    errors = 0
    for target in recipients:
        try:
            await bot.send_message(
                target,
                body,
                disable_web_page_preview=True,
                parse_mode=None,
            )
            ok += 1
        except Exception:
            errors += 1
        await asyncio.sleep(0.035)

    await state.clear()
    await prog.edit_text(
        f"Готово. Доставлено: {ok}, ошибок отправки: {errors}.",
        parse_mode=None,
    )

"""Раздел «Чаты»: память и управление историей."""

import html

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from database import Database
from keyboards.user_menu import MENU_CB_CHATS
from services.admin_rights import is_admin

router = Router(name="chats")

CHAT_CB_SHOW = "chats:show"
CHAT_CB_CLEAR = "chats:clear"
CHAT_CB_BIZ_AUTOREPLY_TOGGLE = "chats:biz:toggle"


async def chats_inline_keyboard(db: Database, user_id: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="📜 Показать последние сообщения", callback_data=CHAT_CB_SHOW)],
        [InlineKeyboardButton(text="🧹 Очистить память", callback_data=CHAT_CB_CLEAR)],
    ]
    if is_admin(user_id):
        enabled = await db.get_admin_business_autoreply_enabled()
        status = "ON" if enabled else "OFF"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🤖 Автоответ Business Connect: {status}",
                    callback_data=CHAT_CB_BIZ_AUTOREPLY_TOGGLE,
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == MENU_CB_CHATS)
async def chats_menu_cb(query: CallbackQuery, db: Database) -> None:
    await query.answer()
    if not query.message:
        return
    uid = query.from_user.id if query.from_user else 0
    note = ""
    if is_admin(uid):
        note = (
            "\n\n<b>Business Connect (только админ)</b>\n"
            "Включите автоответ, и бот сможет отвечать за вас в подключенном бизнес-аккаунте."
        )
    await query.message.answer(
        "💬 <b>Чаты</b>\n\n"
        "Здесь хранится краткая память диалога, чтобы бот помнил контекст прошлых сообщений.\n"
        "Вы можете посмотреть последние записи или очистить память."
        + note,
        parse_mode="HTML",
        reply_markup=await chats_inline_keyboard(db, uid),
    )


@router.callback_query(F.data == CHAT_CB_SHOW)
async def chats_show_cb(query: CallbackQuery, db: Database) -> None:
    await query.answer()
    if not query.message:
        return
    uid = query.from_user.id if query.from_user else 0
    rows = await db.get_recent_chat_messages(uid, limit=12)
    if not rows:
        await query.message.answer("Память чата пока пустая.")
        return

    parts = ["📜 <b>Последние сообщения в памяти</b>\n"]
    for row in rows[-8:]:
        role = "Вы" if row["role"] == "user" else "Qubit"
        txt = str(row["content"]).strip().replace("\n", " ")
        if len(txt) > 180:
            txt = txt[:177] + "..."
        parts.append(f"• <b>{role}:</b> {html.escape(txt)}")

    await query.message.answer("\n".join(parts), parse_mode="HTML")


@router.callback_query(F.data == CHAT_CB_CLEAR)
async def chats_clear_cb(query: CallbackQuery, db: Database) -> None:
    await query.answer()
    if not query.message:
        return
    uid = query.from_user.id if query.from_user else 0
    deleted = await db.clear_chat_messages(uid)
    await query.message.answer(
        f"🧹 Память очищена. Удалено записей: <b>{deleted}</b>.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == CHAT_CB_BIZ_AUTOREPLY_TOGGLE)
async def chats_biz_toggle_cb(query: CallbackQuery, db: Database) -> None:
    await query.answer()
    if not query.message:
        return
    uid = query.from_user.id if query.from_user else 0
    if not is_admin(uid):
        await query.answer("Только для админа", show_alert=True)
        return

    current = await db.get_admin_business_autoreply_enabled()
    new_state = not current
    await db.set_admin_business_autoreply_enabled(new_state)
    state_txt = "включен" if new_state else "выключен"
    await query.message.answer(
        "⚙️ Режим автоответа Business Connect <b>"
        + state_txt
        + "</b>.\n\n"
        "Чтобы работало, подключите бота в Telegram: "
        "<i>Настройки > Автоматизация чатов</i> и разрешите доступ к нужным чатам.",
        parse_mode="HTML",
        reply_markup=await chats_inline_keyboard(db, uid),
    )

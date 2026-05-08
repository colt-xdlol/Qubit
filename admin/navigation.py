"""Вход и выход из админ-панели."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards.admin_menu import admin_panel_keyboard
from keyboards.user_menu import MENU_CB_ADMIN
from services.admin_rights import is_admin
from services.menu_screen import send_main_menu_screen

BACK_BTN = "◀️ Выход из админки"

router = Router(name="admin_nav")


@router.callback_query(F.data == MENU_CB_ADMIN)
async def open_panel_cb(query: CallbackQuery) -> None:
    uid = query.from_user.id if query.from_user else 0
    if query.message is None:
        await query.answer()
        return
    if not is_admin(uid):
        await query.answer("Недоступно", show_alert=True)
        return
    await query.answer()
    await query.message.answer(
        "<b>Административная консоль Qubit</b>\n\n"
        "Дальше команды нижней инлайн/Reply‑панели; выход через «Выход из админки».",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == BACK_BTN)
async def leave_panel(message: Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return
    await send_main_menu_screen(
        message.bot,
        chat_id=message.chat.id,
        user_id=uid,
        cleanup_reply_keyboard=True,
    )

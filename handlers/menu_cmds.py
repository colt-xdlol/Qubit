"""Команды для отображения главного меню."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.user_menu import MENU_CB_BACK
from services.menu_screen import send_main_menu_screen

router = Router(name="menu_cmds")


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    await send_main_menu_screen(
        message.bot,
        chat_id=message.chat.id,
        user_id=uid,
        cleanup_reply_keyboard=True,
    )


@router.callback_query(F.data == MENU_CB_BACK)
async def back_to_menu(query: CallbackQuery) -> None:
    """Возврат в главное меню — отправляем новое фото."""
    await query.answer()
    if not query.message:
        return
    uid = query.from_user.id if query.from_user else 0
    await send_main_menu_screen(
        query.bot,
        chat_id=query.message.chat.id,
        user_id=uid,
    )
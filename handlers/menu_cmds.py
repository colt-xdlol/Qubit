"""Команды для отображения главного меню."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

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

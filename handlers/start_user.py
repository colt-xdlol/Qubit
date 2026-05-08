"""Команда /start, регистрация и реферальный параметр."""

from datetime import datetime, timezone

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from database import Database
from services.menu_screen import send_main_menu_screen
from services.referral_service import parse_ref_start_arg, deep_link

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, db: Database) -> None:
    uid = message.from_user.id if message.from_user else 0
    name = (
        message.from_user.full_name
        if message.from_user
        else "Пользователь"
    )
    uname = message.from_user.username if message.from_user else None

    now = datetime.now(timezone.utc).isoformat()
    await db.upsert_user(uid, uname, name, now)

    arg = ""
    if message.text and " " in message.text:
        arg = message.text.split(maxsplit=1)[1].strip()

    ref_id = parse_ref_start_arg(arg)
    ref_ok = False
    if ref_id is not None and ref_id != uid:
        ref_ok = await db.add_referral_if_new(ref_id, uid, now)

    greet = (
        "Привет! Я — <b>Qubit</b>, ваш AI‑помощник в Telegram.\n\n"
        "Пишите любой вопрос сообщением в этот чат — я отвечу подробным, "
        "структурированным текстом.\n"
        "⚡️ <b>Плавный вывод ответов:</b> сообщение появляется постепенно по мере генерации.\n\n"
        "<b>Навигация</b>: на изображении ниже — инлайн‑кнопки. "
        "Команда <code>/menu</code> снова откроет панель меню."
    )
    if ref_ok:
        greet += "\n\n🎁 Вы перешли по реферальной ссылке. Спасибо за регистрацию!"

    link = await deep_link(bot, uid)
    greet += f"\n\n🔗 Ваша персональная ссылка:\n<code>{link}</code>"

    await message.answer(greet, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    await send_main_menu_screen(
        bot,
        chat_id=message.chat.id,
        user_id=uid,
        cleanup_reply_keyboard=False,
    )

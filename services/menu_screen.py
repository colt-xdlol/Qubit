"""Главный экран: фото меню и инлайн-кнопки."""

from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, ReplyKeyboardRemove

from config import settings
from keyboards.user_menu import main_inline_keyboard

PROJECT_ROOT = Path(__file__).resolve().parents[1]


async def send_main_menu_screen(
    bot: Bot,
    *,
    chat_id: int,
    user_id: int,
    cleanup_reply_keyboard: bool = False,
) -> None:
    """
    Если cleanup_reply_keyboard=True — удаляем нижнюю («Reply») клавиатуру (напр. после админ-панели).
    """
    if cleanup_reply_keyboard:
        await bot.send_message(
            chat_id,
            "\u2063",
            reply_markup=ReplyKeyboardRemove(),
            disable_notification=True,
        )

    rel = Path(settings.menu_image_path)
    img_path = rel if rel.is_absolute() else (PROJECT_ROOT / rel)
    caption = (
        "<b>Qubit</b>\n\n"
        "Выберите раздел ниже или напишите вопрос текстом — на него ответит нейросеть.\n"
        "Для управления памятью диалогов откройте раздел <b>«Чаты»</b>."
    )
    kb = main_inline_keyboard(user_id)

    if img_path.is_file():
        await bot.send_photo(
            chat_id,
            photo=FSInputFile(img_path),
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML",
        )
    else:
        await bot.send_message(
            chat_id,
            caption
            + f"\n\n<i>Файл меню ({settings.menu_image_path}) не найден — добавьте изображение и перезапустите бота.</i>",
            reply_markup=kb,
            parse_mode="HTML",
        )

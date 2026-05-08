"""Клавиатуры админ-панели."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_panel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📈 Статистика"), KeyboardButton(text="📣 Рассылка")],
            [
                KeyboardButton(text="⛔ Бан пользователя"),
                KeyboardButton(text="✅ Разбан"),
            ],
            [
                KeyboardButton(text="➕ Бонус запросов"),
                KeyboardButton(text="🔢 Установить бонус"),
            ],
            [KeyboardButton(text="◀️ Выход из админки")],
        ],
        resize_keyboard=True,
    )

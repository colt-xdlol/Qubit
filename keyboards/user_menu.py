"""Инлайн-меню Qubit."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import settings
from services.admin_rights import is_admin

FAQ_CALLBACK_PREFIX = "faq:"

MENU_CB_LIMIT = "menu:limit"
MENU_CB_REFS = "menu:refs"
MENU_CB_BUY = "menu:buy"
MENU_CB_CHATS = "menu:chats"
MENU_CB_FAQ = "menu:faq"
MENU_CB_SUPPORT = "menu:support"
MENU_CB_ADMIN = "menu:admin"
MENU_CB_BACK = "menu:back"


def main_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="📊 Мой лимит",
                callback_data=MENU_CB_LIMIT,
            ),
            InlineKeyboardButton(text="🤝 Рефералы", callback_data=MENU_CB_REFS),
        ],
        [
            InlineKeyboardButton(text="💳 Купить запросы", callback_data=MENU_CB_BUY),
        ],
        [
            InlineKeyboardButton(text="💬 Чаты", callback_data=MENU_CB_CHATS),
        ],
        [
            InlineKeyboardButton(text="❓ FAQ", callback_data=MENU_CB_FAQ),
            InlineKeyboardButton(text="📞 Поддержка", callback_data=MENU_CB_SUPPORT),
        ],
    ]
    if is_admin(user_id):
        rows.append(
            [
                InlineKeyboardButton(
                    text="⚙️ Админ-панель",
                    callback_data=MENU_CB_ADMIN,
                ),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_button_inline_keyboard(
    back_callback: str = MENU_CB_BACK,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=back_callback,
                ),
            ],
        ],
    )


def faq_inline_keyboard() -> InlineKeyboardMarkup:
    support = settings.support_username.lstrip("@")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Как работает лимит?",
                    callback_data=f"{FAQ_CALLBACK_PREFIX}limit",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Реферальная программа",
                    callback_data=f"{FAQ_CALLBACK_PREFIX}refs",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Оплата и ЮMoney",
                    callback_data=f"{FAQ_CALLBACK_PREFIX}pay",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Написать в поддержку",
                    url=f"https://t.me/{support}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MENU_CB_BACK,
                ),
            ],
        ]
    )
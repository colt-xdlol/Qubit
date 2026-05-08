"""Блокирует забаненных пользователей."""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class BanGateMiddleware(BaseMiddleware):
    def __init__(self, db) -> None:
        self._db = db

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        uid: int | None = None
        if isinstance(event, Message) and event.from_user:
            uid = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            uid = event.from_user.id
        if uid is None:
            return await handler(event, data)
        row = await self._db.get_user_row(uid)
        if row and row["is_banned"]:
            if isinstance(event, Message):
                await event.answer(
                    "⛔ Ваш аккаунт заблокирован. Обратитесь в техподдержку."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Аккаунт заблокирован.", show_alert=True)
            return None
        return await handler(event, data)

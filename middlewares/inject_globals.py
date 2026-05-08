"""Прокидывает сервисы в data хендлеров."""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware

from database import Database
from services.groq_service import GroqService


class InjectGlobalsMiddleware(BaseMiddleware):
    def __init__(
        self,
        db: Database,
        groq: GroqService,
    ) -> None:
        self._db = db
        self._groq = groq

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        data["db"] = self._db
        data["groq"] = self._groq
        return await handler(event, data)

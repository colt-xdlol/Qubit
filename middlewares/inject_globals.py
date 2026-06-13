"""Прокидывает сервисы в data хендлеров."""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware

from database import Database
from services.routerai_service import RouterAIService


class InjectGlobalsMiddleware(BaseMiddleware):
    def __init__(
        self,
        db: Database,
        ai: RouterAIService,
    ) -> None:
        self._db = db
        self._ai = ai

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        data["db"] = self._db
        data["ai"] = self._ai
        return await handler(event, data)

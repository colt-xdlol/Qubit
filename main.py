"""Запуск бота Qubit (aiogram 3 + RouterAI)."""

import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from admin import build_admin_router
from config import settings
from database import Database
from handlers import build_user_router
from middlewares.ban_gate import BanGateMiddleware
from middlewares.inject_globals import InjectGlobalsMiddleware
from services.routerai_service import RouterAIService
from services.yoomoney_webhook_app import run_yoomoney_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


async def main() -> None:
    bot = Bot(
        settings.bot_token,
        default=DefaultBotProperties(),
    )
    db = Database()
    ai = RouterAIService(
        api_key=settings.routerai_api_key,
        base_url=settings.routerai_base_url,
        model=settings.routerai_model,
    )

    await db.connect()

    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(InjectGlobalsMiddleware(db=db, ai=ai))
    dp.message.middleware(BanGateMiddleware(db))
    dp.callback_query.middleware(BanGateMiddleware(db))

    dp.include_router(build_admin_router())
    dp.include_router(build_user_router())

    logging.info(
        "Qubit polling… timezone=%s daily_free=%s model=%s",
        settings.timezone,
        settings.daily_free_limit,
        settings.routerai_model,
    )

    stop_webhook = asyncio.Event()
    webhook_task = asyncio.create_task(
        run_yoomoney_server(bot=bot, db=db, stop_event=stop_webhook),
    )

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        stop_webhook.set()
        try:
            await asyncio.wait_for(webhook_task, timeout=25)
        except asyncio.TimeoutError:
            webhook_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await webhook_task
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

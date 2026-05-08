"""HTTP-сервер для входящих уведомлений ЮMoney (aiohttp), параллельно Telegram polling."""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from aiohttp import web

from config import settings
from database import Database
from services.yoomoney_sign import notification_sign_ok

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


def truthy(raw: str) -> bool:
    return raw.casefold() in {"1", "true", "yes", "on"}


def webhook_full_url_hint() -> str:
    root = settings.public_base_url.strip().rstrip("/")
    if not root:
        return "(укажите PUBLIC_BASE_URL в .env, например https://bot.example.com)"
    return f"{root}{settings.yoomoney_webhook_path}"


async def handle_yoomoney_notify(request: web.Request) -> web.Response:
    if request.method.upper() != "POST":
        return web.Response(status=405, text="method not allowed")

    post = await request.post()
    params = {str(k): str(v) for k, v in post.items()}

    bot: Bot | None = request.app.get("bot")
    db: Database | None = request.app.get("db")
    if db is None or bot is None:
        logger.error("Webhook app без bot/db")
        return web.Response(status=500, text="server misconfigured")

    recv_sign = params.get("sign")
    if recv_sign is None:
        logger.warning("Уведомление ЮMoney без sign")
        return web.Response(status=400, text="missing sign")

    if not notification_sign_ok(params):
        logger.warning("Неверная подпись ЮMoney (проверьте YOOMONEY_NOTIFICATION_SECRET)")
        return web.Response(status=403, text="bad signature")

    n_type = params.get("notification_type", "")
    if n_type not in {"p2p-incoming", "card-incoming"}:
        return web.Response(text="ignored type", status=200)

    if truthy(params.get("test_notification", "false")):
        logger.info("Тестовое уведомление ЮMoney (без начисления)")
        return web.Response(text="OK", status=200)

    label = params.get("label", "") or ""
    raw_amount = params.get("amount", "")
    operation_id = (params.get("operation_id", "") or "").strip()
    if not operation_id:
        logger.warning("Уведомление ЮMoney без operation_id")
        return web.Response(status=400, text="missing operation_id")
    if not label:
        logger.warning("Уведомление ЮMoney без label")
        return web.Response(status=200, text="ignored empty label")

    try:
        amount_val = float(Decimal(str(raw_amount)))
    except (InvalidOperation, ValueError):
        logger.warning("Некорректная сумма в уведомлении: %r", raw_amount)
        return web.Response(status=400, text="bad amount")

    if amount_val <= 0:
        return web.Response(status=400, text="non-positive amount")

    paid_at_iso = params.get("datetime") or ""

    result = await db.try_fulfill_yoomoney_payment(
        label=label,
        operation_id=operation_id,
        amount_received=amount_val,
        paid_at_iso=paid_at_iso,
    )

    if result == "credited":
        order = await db.get_payment_order(label)
        user_id = int(order["user_id"]) if order else None
        req_n = int(order["requests"]) if order else None
        if user_id:
            msg = (
                "✅ Оплата получена, спасибо!\n\n"
                f"Зачислено запросов: {req_n or '—'}.\n\n"
                "Бонус уже учитывается в «Мой лимит» (к вашей дневной квоте, как приглашения)."
            )
            try:
                await bot.send_message(user_id, msg)
            except Exception:
                logger.exception(
                    "Не удалось отправить подтверждение пользователю %s",
                    user_id,
                )

    logger.info(
        "ЮMoney notify label=%s op=%s amt=%s result=%s",
        label,
        operation_id,
        amount_val,
        result,
    )
    return web.Response(text="OK", status=200)


def create_yoomoney_app(*, bot: Bot, db: Database) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app["db"] = db
    path = settings.yoomoney_webhook_path
    route_path = path if path.startswith("/") else "/" + path
    app.router.add_post(route_path, handle_yoomoney_notify)
    return app


async def run_yoomoney_server(*, bot: Bot, db: Database, stop_event: asyncio.Event) -> None:
    """Слушает вебхук до установки stop_event."""
    if not settings.yoomoney_wallet or not settings.yoomoney_notification_secret:
        await stop_event.wait()
        return

    app = create_yoomoney_app(bot=bot, db=db)
    runner = web.AppRunner(app)
    await runner.setup()
    host = settings.yoomoney_webhook_host
    port = int(settings.yoomoney_webhook_port)
    site = web.TCPSite(runner, host=host, port=port)

    route_path = (
        settings.yoomoney_webhook_path
        if settings.yoomoney_webhook_path.startswith("/")
        else "/" + settings.yoomoney_webhook_path
    )
    try:
        await site.start()
        logger.info(
            "ЮMoney webhook слушает http://%s:%s%s — укажите этот путь после HTTPS‑прокси в настройках кошелька: %s",
            host,
            port,
            route_path,
            webhook_full_url_hint(),
        )
        await stop_event.wait()
    finally:
        await site.stop()
        await runner.cleanup()

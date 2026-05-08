"""Покупка дополнительных запросов через Telegram Stars."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from config import settings
from database import Database
from keyboards.user_menu import MENU_CB_BUY
from states.payment_fsm import PaymentFlow

router = Router(name="payments")


def _payments_enabled() -> bool:
    return settings.price_per_request_stars > 0


def build_qty_keyboard(*, presets: tuple[int, ...]) -> InlineKeyboardMarkup:
    row: list[list[InlineKeyboardButton]] = []
    buf: list[InlineKeyboardButton] = []
    p = settings.price_per_request_stars
    for n in presets:
        txt = f"{n} × {p}⭐ → {n * p}⭐"
        buf.append(InlineKeyboardButton(text=txt, callback_data=f"bq:{n}"))
        if len(buf) == 2:
            row.append(buf)
            buf = []
    if buf:
        row.append(buf)
    row.append(
        [
            InlineKeyboardButton(
                text="Своё число…",
                callback_data="bq:custom",
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=row)


PRESETS = (1, 3, 5, 10, 25, 50)


async def _issue_invoice_reply(message: Message, db: Database, qty: int) -> None:
    uid = message.from_user.id if message.from_user else 0
    price = int(settings.price_per_request_stars)
    total = int(qty) * price
    label = uuid4().hex
    now = datetime.now(timezone.utc).isoformat()

    await db.create_payment_order(
        label=label,
        user_id=uid,
        requests=qty,
        amount_rub=float(total),
        created_at_iso=now,
    )
    await message.answer_invoice(
        title="Покупка запросов",
        description=f"Пакет: {qty} дополнительных запросов",
        payload=label,
        currency="XTR",
        prices=[LabeledPrice(label=f"{qty} запросов", amount=total)],
    )


@router.callback_query(F.data == MENU_CB_BUY)
async def open_buy_menu_cb(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    if query.message is None:
        return
    await state.clear()

    if not _payments_enabled():
        await query.message.answer(
            "Платежи отключены: установите положительное значение <code>PRICE_PER_REQUEST_STARS</code> в <code>.env</code>.",
            parse_mode="HTML",
        )
        return

    kb = build_qty_keyboard(presets=PRESETS)
    await query.message.answer(
        "Выберите, сколько <b>дополнительных запросов</b> хотите докупить, "
        f"или введите своё число (до <code>{settings.payment_qty_max}</code>). "
        "После выбора бот отправит Telegram-инвойс в ⭐ Stars.\n\n"
        "<i>Свой объём после кнопки «Своё число» — следующим сообщением.</i>",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("bq:"))
async def buy_qty_callback(query: CallbackQuery, state: FSMContext, db: Database) -> None:
    await query.answer()
    if query.message is None:
        return
    if not _payments_enabled():
        await query.message.answer("Оплата отключена в настройках бота.")
        return

    payload = query.data.split(":", maxsplit=1)[1]
    if payload == "custom":
        await state.set_state(PaymentFlow.awaiting_custom_qty)
        await query.message.answer(
            f"Введите целое число запросов от <code>1</code> до <code>{settings.payment_qty_max}</code>.\n\n"
            "Отмена: /cancel_buy",
            parse_mode="HTML",
        )
        return

    try:
        qty = int(payload)
    except ValueError:
        await query.message.answer("Некорректный выбор.")
        return

    if not (1 <= qty <= settings.payment_qty_max):
        await query.message.answer("Количество вне допустимого диапазона.")
        return

    await state.clear()
    await _issue_invoice_reply(query.message, db, qty)


@router.message(PaymentFlow.awaiting_custom_qty, Command("cancel_buy"))
async def cancel_custom_qty(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Покупка отменена.")


@router.message(PaymentFlow.awaiting_custom_qty, F.text.regexp(r"^[1-9]\d*$"))
async def custom_qty_entered(message: Message, state: FSMContext, db: Database) -> None:
    qty = int(message.text.strip())
    if qty > settings.payment_qty_max:
        await message.answer(
            f"Слишком много. Максимум за один раз: {settings.payment_qty_max}.",
        )
        return

    await state.clear()
    await _issue_invoice_reply(message, db, qty)


@router.message(PaymentFlow.awaiting_custom_qty)
async def bad_custom_qty(message: Message) -> None:
    await message.answer("Нужно целое число без пробелов. Отмена: /cancel_buy")


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, db: Database) -> None:
    label = pre_checkout_query.invoice_payload
    order = await db.get_payment_order(label)
    if order is None:
        await pre_checkout_query.answer(ok=False, error_message="Счёт не найден. Попробуйте снова.")
        return
    if str(order["status"]) != "pending":
        await pre_checkout_query.answer(ok=False, error_message="Счёт уже обработан.")
        return
    expected_total = int(float(order["amount_rub"]))
    if int(pre_checkout_query.total_amount) != expected_total:
        await pre_checkout_query.answer(ok=False, error_message="Сумма счёта изменилась. Оформите покупку заново.")
        return
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, db: Database) -> None:
    payment = message.successful_payment
    if payment is None:
        return

    charge_id = payment.telegram_payment_charge_id.strip()
    result = await db.try_fulfill_yoomoney_payment(
        label=payment.invoice_payload,
        operation_id=charge_id,
        amount_received=float(payment.total_amount),
        paid_at_iso=datetime.now(timezone.utc).isoformat(),
        amount_tolerance=0.0,
    )

    if result == "credited":
        await message.answer(
            "✅ Оплата прошла успешно.\n"
            "Дополнительные запросы зачислены и уже доступны в вашем лимите."
        )
        return
    if result == "duplicate_op":
        await message.answer("Платёж уже обработан.")
        return

    await message.answer(
        "Оплата получена, но не удалось автоматически зачислить запросы.\n"
        "Напишите в поддержку: @"
        + settings.support_username.lstrip("@")
    )

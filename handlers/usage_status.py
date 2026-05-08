"""Подробности по лимиту запросов (раздел «Мой лимит»)."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database import Database
from keyboards.user_menu import MENU_CB_LIMIT
from services.quota_service import quota_snapshot

router = Router(name="usage_status")


@router.callback_query(F.data == MENU_CB_LIMIT)
async def show_limit_cb(query: CallbackQuery, db: Database) -> None:
    await query.answer()
    if not query.message:
        return
    uid = query.from_user.id if query.from_user else 0
    snap = await quota_snapshot(db, uid)

    if snap.unlimited:
        await query.message.answer(
            "👑 <b>Вы администратор</b>\n\n"
            "Суточные лимиты для вас не применяются — можно задавать вопросы без ограничений.",
            parse_mode="HTML",
        )
        return

    text = (
        "📊 <b>Ваш лимит на сегодня</b>\n\n"
        f"• Использовано: <b>{snap.used_today}</b> из <b>{snap.total_limit_today}</b>\n"
        f"• Осталось: <b>{snap.remaining}</b>\n\n"
        f"Бесплатная база: <b>{snap.daily_base}</b> запросов в сутки (часовой пояс бота).\n"
        f"Бонус к лимиту (<i>рефералы + покупки</i>): <b>+{snap.referral_bonus}</b> "
        "к максимуму на каждый день.\n\n"
        "<i>Счётчик обнуляется при наступлении нового календарного дня в этой зоне.</i>"
    )
    await query.message.answer(text, parse_mode="HTML")

"""Рефералы: статистика и ссылка."""

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from database import Database
from keyboards.user_menu import MENU_CB_REFS
from services.referral_service import deep_link

router = Router(name="referrals")


@router.callback_query(F.data == MENU_CB_REFS)
async def show_referrals_cb(query: CallbackQuery, bot: Bot, db: Database) -> None:
    await query.answer()
    if not query.message:
        return
    uid = query.from_user.id if query.from_user else 0
    cnt = await db.count_referrals(uid)
    link = await deep_link(bot, uid)
    txt = (
        "🤝 <b>Реферальная программа Qubit</b>\n\n"
        "За каждого нового пользователя, который <b>впервые</b> запустил бота по вашей персональной ссылке, "
        "вы получаете <b>+1</b> к дневному лимиту на каждый день навсегда (суммируется с каждым человеком).\n\n"
        f"Приглашено: <b>{cnt}</b> чел.\n\n"
        f"Ваша ссылка:\n<code>{link}</code>\n\n"
        "<i>Покупку запросов можно оформить из меню («Купить запросы»).</i>"
    )
    await query.message.answer(txt, parse_mode="HTML")

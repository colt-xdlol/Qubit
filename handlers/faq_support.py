"""FAQ, подсказки и контакт техподдержки."""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import settings
from keyboards.user_menu import (
    FAQ_CALLBACK_PREFIX,
    MENU_CB_FAQ,
    MENU_CB_SUPPORT,
    back_button_inline_keyboard,
    faq_inline_keyboard,
)

router = Router(name="faq_support")


FAQ_INTRO = (
    "<b>❓ Частые вопросы (FAQ)</b>\n\n"
    "Выберите тему ниже или напишите в поддержку — там подскажут по работе бота."
)


@router.callback_query(F.data == MENU_CB_FAQ)
async def faq_intro_cb(query: CallbackQuery) -> None:
    await query.answer()
    if not query.message:
        return
    await query.message.answer(
        FAQ_INTRO,
        parse_mode="HTML",
        reply_markup=faq_inline_keyboard(),
    )


@router.callback_query(F.data == "faq:limit")
async def faq_limit_cb(query: CallbackQuery) -> None:
    await query.answer()
    if not query.message:
        return
    txt = (
        "<b>Как устроен дневной лимит?</b>\n\n"
        "1. У каждого пользователя есть <b>базовый бесплатный пакет</b> (по умолчанию 10 ответов за сутки "
        "по дате в часовом поясе бота).\n"
        "2. Лимит <b>обнуляется</b> с новым календарным днём — счётчик «сколько уже спросили сегодня» сбрасывается.\n"
        "3. <b>Бонус</b> от рефералов и покупок <b>сохраняется</b> и увеличивает ваш максимум на каждый день.\n"
        "4. <b>Администраторы</b> не ограничены.\n\n"
        "Нужно больше доступа — кнопка «Купить запросы» или реферальная ссылка. "
        "По крупным вопросам: @"
        + settings.support_username.lstrip("@")
        + "."
    )
    await query.message.answer(
        txt,
        parse_mode="HTML",
        reply_markup=back_button_inline_keyboard(back_callback=f"{FAQ_CALLBACK_PREFIX}back"),
    )


@router.callback_query(F.data == "faq:refs")
async def faq_refs_cb(query: CallbackQuery) -> None:
    await query.answer()
    if not query.message:
        return
    txt = (
        "<b>Реферальная система</b>\n\n"
        "• У вас есть уникальная ссылка в разделе «Рефералы».\n"
        "• Когда человек <b>впервые</b> активирует бота по ней как новый пользователь, вы получаете "
        "<b>+1</b> к дневному лимиту (навсегда, на каждый день отдельно).\n"
        "• Если приглашённый уже был в боте, повторное начисление не делается."
    )
    await query.message.answer(
        txt,
        parse_mode="HTML",
        reply_markup=back_button_inline_keyboard(back_callback=f"{FAQ_CALLBACK_PREFIX}back"),
    )


@router.callback_query(F.data == "faq:pay")
async def faq_pay_cb(query: CallbackQuery) -> None:
    await query.answer()
    if not query.message:
        return
    txt = (
        "<b>Оплата через Telegram Stars</b>\n\n"
        f"• В меню есть «Купить запросы». Тариф задаётся владельцем бота: <code>{settings.price_per_request_stars}</code> ⭐ за запрос "
        "(через <code>PRICE_PER_REQUEST_STARS</code> в <code>.env</code>).\n"
        "• После выбора количества бот отправляет встроенный Telegram-инвойс.\n"
        "• После успешной оплаты запросы начисляются автоматически и сразу видны в «Мой лимит».\n"
        "• Технический <code>payload</code> сохраняется только для безопасной привязки платежа к вашему аккаунту."
    )
    await query.message.answer(
        txt,
        parse_mode="HTML",
        reply_markup=back_button_inline_keyboard(back_callback=f"{FAQ_CALLBACK_PREFIX}back"),
    )


@router.callback_query(F.data == f"{FAQ_CALLBACK_PREFIX}back")
async def faq_back_cb(query: CallbackQuery) -> None:
    await query.answer()
    if not query.message:
        return
    await query.message.answer(
        FAQ_INTRO,
        parse_mode="HTML",
        reply_markup=faq_inline_keyboard(),
    )


@router.callback_query(F.data == MENU_CB_SUPPORT)
async def support_route_cb(query: CallbackQuery) -> None:
    await query.answer()
    if not query.message:
        return
    su = settings.support_username.lstrip("@")
    txt = (
        "<b>📞 Техническая поддержка</b>\n\n"
        f"Напрямую: @{su}\n\n"
        "<b>Когда писать:</b> ошибки бота, доступ, платные задачи после оплаты, разблокировки.\n"
        "<b>Как писать:</b> шаги, время проблемы, ваш user id (его видно в профиле Telegram).\n\n"
        "Обычные вопросы к искусственному интеллекту — просто текстом в чат, они не уходят в поддержку по умолчанию."
    )
    await query.message.answer(
        txt,
        parse_mode="HTML",
        reply_markup=back_button_inline_keyboard(),
    )
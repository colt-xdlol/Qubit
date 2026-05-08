"""Сводка по базе данных."""

from aiogram import F, Router
from aiogram.types import Message

from database import Database
from services.admin_rights import is_admin
from services.quota_service import quota_snapshot


router = Router(name="admin_stats")


STAT_BTN = "📈 Статистика"


@router.message(F.text == STAT_BTN)
async def admin_statistics(message: Message, db: Database) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return

    users = await db.total_users()
    raw_sum = await db.total_requests_today_sum()

    txt = (
        "**📈 Сводка**\n\n"
        f"*Пользователей в базе:* `{users}`\n"
        f"*Σ запросов (сохранённые счётчики «сегодня» после последнего взаимодействия):* `{raw_sum}`\n\n"
        "`Примечание.` Агрегат отражает хранящиеся счётчики в таблице. Для живой аналитики по дням "
        "лучше вынести логирование во внешнюю базу временных рядов."
    )

    demo = await quota_snapshot(db, uid)
    txt += (
        "\n\n*Пример вашей квоты:* безлимит "
        + ("активирован" if demo.unlimited else f"нет ({demo.remaining} оставшихся)")
    )

    await message.answer(txt, parse_mode="Markdown")

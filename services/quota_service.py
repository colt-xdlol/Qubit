"""Дневной лимит запросов и бонус от рефералов."""

from dataclasses import dataclass

from config import settings
from database import Database
from services.admin_rights import is_admin
from services.date_utils import today_str


@dataclass(slots=True)
class QuotaSnapshot:
    remaining: int
    used_today: int
    daily_base: int
    referral_bonus: int
    total_limit_today: int
    unlimited: bool


async def quota_snapshot(db: Database, user_id: int) -> QuotaSnapshot:
    if is_admin(user_id):
        return QuotaSnapshot(-1, 0, settings.daily_free_limit, 0, -1, True)

    day = today_str(settings.timezone)
    used, referral_bonus = await db.reset_daily_counter_if_needed(user_id, day)
    total = settings.daily_free_limit + int(referral_bonus)
    remaining = max(0, total - int(used))
    return QuotaSnapshot(
        remaining=remaining,
        used_today=int(used),
        daily_base=settings.daily_free_limit,
        referral_bonus=int(referral_bonus),
        total_limit_today=total,
        unlimited=False,
    )


async def get_remaining_and_limit(
    db: Database,
    user_id: int,
) -> tuple[int, int, bool]:
    snap = await quota_snapshot(db, user_id)
    if snap.unlimited:
        return -1, -1, True
    return snap.remaining, snap.total_limit_today, False


async def can_make_request(db: Database, user_id: int) -> bool:
    if is_admin(user_id):
        return True
    day = today_str(settings.timezone)
    used, bonus = await db.reset_daily_counter_if_needed(user_id, day)
    limit = settings.daily_free_limit + int(bonus)
    return used < limit


async def record_successful_ai_request(db: Database, user_id: int) -> None:
    if is_admin(user_id):
        return
    day = today_str(settings.timezone)
    await db.increment_usage(user_id, day)

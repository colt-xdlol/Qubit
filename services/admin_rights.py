"""Проверка прав администратора."""

from config import settings


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_set

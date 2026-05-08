"""Дата в выбранном часовом поясе."""

from datetime import datetime
from zoneinfo import ZoneInfo


def today_str(tz: str) -> str:
    dt = datetime.now(ZoneInfo(tz))
    return dt.strftime("%Y-%m-%d")

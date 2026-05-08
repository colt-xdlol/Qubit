"""Реферальные ссылки и начисление бонуса."""

from aiogram import Bot


def build_ref_payload(inviter_id: int) -> str:
    return f"ref_{inviter_id}"


def parse_ref_start_arg(arg: str | None) -> int | None:
    if not arg:
        return None
    if arg.startswith("ref_"):
        raw = arg[4:]
        if raw.isdigit():
            return int(raw)
    return None


async def deep_link(bot: Bot, inviter_id: int) -> str:
    me = await bot.get_me()
    if not me.username:
        return "Сначала задайте постоянное @имя боту через @BotFather — без него ссылка недоступна."
    payload = build_ref_payload(inviter_id)
    return f"https://t.me/{me.username}?start={payload}"

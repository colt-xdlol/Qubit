"""Бан, разбан и ручное изменение реф-бонуса."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import Database
from services.admin_rights import is_admin
from states.admin_fsm import AdminFlow

router = Router(name="admin_mod")

BAN_BTN = "⛔ Бан пользователя"
UNBAN_BTN = "✅ Разбан"
ADD_BONUS_BTN = "➕ Бонус запросов"
SET_BONUS_BTN = "🔢 Установить бонус"


@router.message(F.text == BAN_BTN)
async def prompt_ban(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return
    await state.set_state(AdminFlow.ban_waiting_id)
    await message.answer("Укажите numeric user id для бана текстом одним сообщением.")


@router.message(AdminFlow.ban_waiting_id, F.text.regexp(r"^\d+$"))
async def exec_ban(message: Message, db: Database, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        await state.clear()
        return
    victim = int(message.text.strip())
    await db.set_banned(victim, True)
    await state.clear()
    await message.answer(f"Пользователь `{victim}` заблокирован.", parse_mode="Markdown")


@router.message(AdminFlow.ban_waiting_id)
async def bad_ban_fmt(message: Message, state: FSMContext) -> None:
    uid_op = message.from_user.id if message.from_user else 0
    if not is_admin(uid_op):
        await state.clear()
        return
    await message.answer("Нужно только числовой telegram id, без пробелов.")


@router.message(F.text == UNBAN_BTN)
async def prompt_unban(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return
    await state.set_state(AdminFlow.unban_waiting_id)
    await message.answer("Пришлите numeric user id для разблокировки.")


@router.message(AdminFlow.unban_waiting_id, F.text.regexp(r"^\d+$"))
async def exec_unban(message: Message, db: Database, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        await state.clear()
        return
    victim = int(message.text.strip())
    await db.set_banned(victim, False)
    await state.clear()
    await message.answer(f"Пользователь `{victim}` разблокирован.", parse_mode="Markdown")


@router.message(AdminFlow.unban_waiting_id)
async def bad_unban_fmt(message: Message, state: FSMContext) -> None:
    uid_op = message.from_user.id if message.from_user else 0
    if not is_admin(uid_op):
        await state.clear()
        return
    await message.answer("Нужно только числовой telegram id, без пробелов.")


@router.message(F.text == ADD_BONUS_BTN)
async def prompt_bonus_add(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return
    await state.set_state(AdminFlow.bonus_add_waiting)
    await message.answer(
        "Формат: `<user_id> <сколько добавить>`\nПример: `912345678 5`",
        parse_mode="Markdown",
    )


@router.message(
    AdminFlow.bonus_add_waiting,
    F.text.regexp(r"^\d+\s+[+-]?\d+$"),
)
async def exec_bonus_add(message: Message, db: Database, state: FSMContext) -> None:
    uid_op = message.from_user.id if message.from_user else 0
    if not is_admin(uid_op):
        await state.clear()
        return
    a, b = message.text.strip().split()
    target = int(a)
    delta = int(b)
    await db.add_bonus_requests(target, delta)
    await state.clear()
    await message.answer(f"На `{target}` начислено `{delta:+d}` к реф-бонусу.", parse_mode="Markdown")


@router.message(AdminFlow.bonus_add_waiting)
async def bad_bonus_add_fmt(message: Message, state: FSMContext) -> None:
    uid_op = message.from_user.id if message.from_user else 0
    if not is_admin(uid_op):
        await state.clear()
        return
    await message.answer(
        "Ожидался формат двух чисел через пробел: user_id количество",
    )


@router.message(F.text == SET_BONUS_BTN)
async def prompt_bonus_set(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    if not is_admin(uid):
        return
    await state.set_state(AdminFlow.bonus_set_waiting)
    await message.answer(
        "Формат: `<user_id> <абсолютное значение бонуса>`\nПример: `912345678 12`",
        parse_mode="Markdown",
    )


@router.message(
    AdminFlow.bonus_set_waiting,
    F.text.regexp(r"^\d+\s+[+-]?\d+$"),
)
async def exec_bonus_set(message: Message, db: Database, state: FSMContext) -> None:
    uid_op = message.from_user.id if message.from_user else 0
    if not is_admin(uid_op):
        await state.clear()
        return
    a, b = message.text.strip().split()
    target = int(a)
    value = int(b)
    await db.set_bonus_requests(target, value)
    await state.clear()
    await message.answer(
        f"Для пользователя `{target}` бонус установлен значением `{value}`.",
        parse_mode="Markdown",
    )


@router.message(AdminFlow.bonus_set_waiting)
async def bad_bonus_set_fmt(message: Message, state: FSMContext) -> None:
    uid_op = message.from_user.id if message.from_user else 0
    if not is_admin(uid_op):
        await state.clear()
        return
    await message.answer(
        "Ожидался формат двух чисел через пробел: user_id новое значение",
    )

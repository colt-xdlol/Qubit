"""Состояния админ-сценариев (broadcast, блокировки, бонусы)."""

from aiogram.fsm.state import State, StatesGroup


class AdminFlow(StatesGroup):
    broadcast_text = State()
    ban_waiting_id = State()
    unban_waiting_id = State()
    bonus_add_waiting = State()
    bonus_set_waiting = State()

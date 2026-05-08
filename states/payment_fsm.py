"""Состояния сценария покупки запросов."""

from aiogram.fsm.state import State, StatesGroup


class PaymentFlow(StatesGroup):
    awaiting_custom_qty = State()

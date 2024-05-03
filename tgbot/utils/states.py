from aiogram.fsm.state import StatesGroup, State


class TraderState(StatesGroup):
    new_card = State()
    refill = State()


class AdminState(StatesGroup):
    settings_change = State()
    change_balance = State()
    add_account = State()

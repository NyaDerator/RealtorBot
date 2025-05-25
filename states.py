from aiogram.fsm.state import State, StatesGroup

class ApplicationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

class AdminStates(StatesGroup):
    waiting_for_admin_id = State()
    waiting_for_remove_admin_id = State()
    waiting_for_config_value = State()
    waiting_for_comment = State()
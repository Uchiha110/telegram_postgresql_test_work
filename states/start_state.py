from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    START_DEAFAULT = State()
    START_TARIFFS_1 = State()
    START_START__ = State()

    BUY_STANDART = State()
    BUY_PREMIUM = State()

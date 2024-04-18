from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    newPersonName = State()
    newPersonQuestion = State()
    fillNumberData = State()
    showNumberData = State()

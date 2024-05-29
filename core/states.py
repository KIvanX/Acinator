from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    newPersonName = State()
    newPersonQuestion = State()
    newPersonPhoto = State()
    showNumberData = State()
    addNewQuestion = State()
    addNewSome = State()

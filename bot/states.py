from aiogram.filters.state import StatesGroup, State


class LanguageChooseState(StatesGroup):
    lang = State()


class RegisterState(StatesGroup):
    pnfl = State()
    fio = State()
    passport = State()
    phone = State()
    accept = State()
    storage = State()

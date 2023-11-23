from aiogram.filters.state import StatesGroup, State


class LanguageChooseState(StatesGroup):
    lang = State()


class RegisterState(StatesGroup):
    pnfl = State()
    fio = State()
    passport = State()
    passport_image = State()
    phone = State()
    accept = State()
    storage = State()
    city = State()
    region = State()


class ListId(StatesGroup):
    id = State()
    passport = State()
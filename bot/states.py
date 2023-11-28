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
    is_id_passport = State()


class ListPassport(StatesGroup):
    passport = State()


class IDStorage(StatesGroup):
    storage = State()
    passport = State()


class CalculatorState(StatesGroup):
    storage = State()
    kg = State()

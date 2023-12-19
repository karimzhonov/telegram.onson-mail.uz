from aiogram.filters.state import State, StatesGroup


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
    phone = State()
    city = State()
    region = State()
    action = State()


class IDStorage(StatesGroup):
    storage = State()
    passport = State()


class CalculatorState(StatesGroup):
    storage = State()
    kg = State()

class OnlineBuy(StatesGroup):
    storage = State()
    menu = State()
    category = State()
    product = State()
    chosen = State()


class FAQState(StatesGroup):
    type = State()
    text = State()
    storage = State()


class InfoState(StatesGroup):
    info = State()
    
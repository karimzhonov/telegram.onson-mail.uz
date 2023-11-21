from aiogram import Dispatcher
from aiogram.filters.command import CommandStart
from bot.states import LanguageChooseState, RegisterState
from bot.filters.db_filter import DbSearchFilter
from bot.text_keywords import SETTINGS, TAKE_ID, INFO
from .start import start, choosed_lang, choose_lang, info
from .register import take_id, entered_fio, entered_passport, entered_phone, entered_pnfl, entered_storage, accepted_creating


def setup(dp: Dispatcher):
    dp.message(CommandStart())(start)
    dp.message(DbSearchFilter(SETTINGS))(choose_lang)
    dp.message(DbSearchFilter(TAKE_ID))(take_id)
    dp.message(DbSearchFilter(INFO))(info)
    dp.message(LanguageChooseState.lang)(choosed_lang)
    dp.message(RegisterState.pnfl)(entered_pnfl)
    dp.message(RegisterState.fio)(entered_fio)
    dp.message(RegisterState.passport)(entered_passport)
    dp.message(RegisterState.phone)(entered_phone)
    dp.message(RegisterState.accept)(accepted_creating)
    dp.message(RegisterState.storage)(entered_storage)
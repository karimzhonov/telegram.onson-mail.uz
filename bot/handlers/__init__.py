from aiogram import Dispatcher, F
from aiogram.types import ContentType as CT
from aiogram.filters.command import CommandStart
from bot.states import LanguageChooseState, RegisterState, ListId
from bot.filters.db_filter import DbSearchFilter
from bot.text_keywords import SETTINGS, TAKE_ID, INFO,LISTID, MENU
from .start import start, choosed_lang, choose_lang, info
from .register import take_id, entered_fio, entered_passport, entered_phone, entered_pnfl, entered_storage, accepted_creating, entered_passport_image, entered_city, entered_region
from .my_ids import my_ids, selected_passport


def setup(dp: Dispatcher):
    dp.message(CommandStart())(start)
    dp.message(DbSearchFilter(MENU))(start)
    dp.message(DbSearchFilter(SETTINGS))(choose_lang)
    dp.message(DbSearchFilter(TAKE_ID))(take_id)
    dp.message(DbSearchFilter(INFO))(info)
    dp.message(LanguageChooseState.lang)(choosed_lang)
    dp.message(RegisterState.pnfl)(entered_pnfl)
    dp.message(RegisterState.fio)(entered_fio)
    dp.message(RegisterState.passport)(entered_passport)
    dp.message(RegisterState.passport_image, F.content_type.in_([CT.PHOTO]))(entered_passport_image)
    dp.message(RegisterState.city)(entered_city)
    dp.message(RegisterState.region)(entered_region)
    dp.message(RegisterState.phone)(entered_phone)
    dp.message(RegisterState.accept)(accepted_creating)
    dp.message(RegisterState.storage)(entered_storage) 
    dp.message(DbSearchFilter(LISTID))(my_ids)
    dp.callback_query(ListId.passport)(selected_passport)

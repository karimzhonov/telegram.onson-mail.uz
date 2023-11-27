import os
from django.conf import settings
from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from bot.models import get_text as _
from bot.text_keywords import ABOUT
from bot.filters.db_filter import DbSearchFilter


def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(ABOUT))(about)


async def about(msg: types.Message, state: FSMContext):
    text = _("about_text", msg.bot.lang)
    await msg.answer_photo(
        types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "bot/assets/images/onson-logo.png")), 
        text)

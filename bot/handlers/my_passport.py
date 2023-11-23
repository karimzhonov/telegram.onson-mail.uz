from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from users.models import ClientId
from bot.text_keywords import MENU, CHECK
from bot.models import get_text as _
from bot.states import ListId
from storages.models import Storage


async def my_passports(msg: types.Message, state: FSMContext):
    pass

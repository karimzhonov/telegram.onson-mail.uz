import os

from aiogram import Dispatcher, types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asgiref.sync import sync_to_async
from django.conf import settings
from orders.models import Order
from bot.filters.db_filter import DbSearchFilter
from bot.filters.prefix import Prefix
from bot.models import LANGUAGES, Info, User
from bot.models import get_text as _
from bot.states import InfoState, LanguageChooseState
from bot.text_keywords import (ABOUT, ACCEPT_URL, ACCPET_BUTTON, CALCULATOR, CHECK, EXIT, EXIT_CONFIRM, FAQ,
                               FOTO_REPORTS, INFO, LISTPASSPORT, MENU, ONLINE_BUY, SETTINGS, STORAGES, TAKE_ID, ORDERS)
from bot.utils import get_file, get_file_url
from users.models import ClientId


def setup(dp: Dispatcher):
    dp.message(CommandStart())(start)
    dp.message(DbSearchFilter(MENU))(start)
    dp.message(DbSearchFilter(SETTINGS))(choose_lang)
    dp.message(DbSearchFilter(INFO))(info_list)
    dp.message(InfoState.info)(info)
    dp.message(DbSearchFilter(ACCPET_BUTTON))(accept_url)
    dp.message(LanguageChooseState.lang)(choosed_lang)
    dp.message(DbSearchFilter(EXIT))(exit)
    dp.callback_query(Prefix(EXIT_CONFIRM))(exit_confirm)
    

async def start(msg: types.Message, state: FSMContext):
    await state.clear()
    if await User.objects.filter(id=msg.from_user.id).aexists():
        return await menu(msg, state)
    await choose_lang(msg, state)


async def menu(msg: types.Message, state: FSMContext):
    await state.clear()
    text = _("menu_text", msg.bot.lang)
    keyboard = await _menu_keyboard(msg)
    await msg.answer_photo(
        types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "bot/assets/images/onson-logo.png")), 
        text, reply_markup=keyboard.as_markup())


async def _menu_keyboard(msg: types.Message, user_id=None):
    user_id = msg.from_user.id if not user_id else user_id
    keyboard = ReplyKeyboardBuilder()
    if await ClientId.objects.filter(user_id=user_id, deleted=False).aexists():
        keyboard.row(types.KeyboardButton(text=_(LISTPASSPORT, msg.bot.lang)))
    else:
        keyboard.row(types.KeyboardButton(text=_(TAKE_ID, msg.bot.lang)))
    keyboard.row(types.KeyboardButton(text=_(ACCPET_BUTTON, msg.bot.lang)), types.KeyboardButton(text=_(STORAGES, msg.bot.lang)), types.KeyboardButton(text=_(FOTO_REPORTS, msg.bot.lang)))
    if await ClientId.objects.filter(user_id=user_id, deleted=False).aexists():
        keyboard.row(types.KeyboardButton(text=_(ONLINE_BUY, msg.bot.lang)), types.KeyboardButton(text=f"{_(ORDERS, msg.bot.lang)} ({await Order.objects.filter(with_online_buy=False, client__clientid__user_id=user_id).acount()})"))
    else:
        keyboard.row(types.KeyboardButton(text=_(ONLINE_BUY, msg.bot.lang)), types.KeyboardButton(text=_(ORDERS, msg.bot.lang)))
    keyboard.row(types.KeyboardButton(text=_(SETTINGS, msg.bot.lang)), types.KeyboardButton(text=_(INFO, msg.bot.lang)), types.KeyboardButton(text=_(CALCULATOR, msg.bot.lang)))
    if await ClientId.objects.filter(user_id=user_id).aexists():
        keyboard.row(types.KeyboardButton(text=_(FAQ, msg.bot.lang)), types.KeyboardButton(text=_(EXIT, msg.bot.lang)))
    else:
        keyboard.row(types.KeyboardButton(text=_(FAQ, msg.bot.lang)))
    return keyboard


async def choose_lang(msg: types.Message, state: FSMContext):
    await state.clear()
    keyboard = ReplyKeyboardBuilder()
    for code, text in LANGUAGES:
        if msg.bot.lang == code:
            text = f"{CHECK} {text}"
        keyboard.row(types.KeyboardButton(text=text))
    
    await msg.answer(_("choose_lang_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(LanguageChooseState.lang)


async def choosed_lang(msg: types.Message, state: FSMContext):
    text: str = msg.text
    for code, ltext in LANGUAGES:
        if ltext in text:
            if await User.objects.filter(id=msg.from_user.id).aexists():
                await User.objects.filter(id=msg.from_user.id).aupdate(lang=code)
            else:
                await User.objects.acreate(
                    id=msg.from_user.id,
                    username=msg.from_user.username,
                    first_name=msg.from_user.first_name,
                    last_name=msg.from_user.last_name,
                    lang=code
                )
            msg.bot.lang = code
            break
    await menu(msg, state)
    

async def info_list(msg: types.Message, state: FSMContext):
    if not await Info.objects.translated(msg.bot.lang).filter(is_active=True).aexists():
        return await msg.answer(_("info_not_upload_yeat", msg.bot.lang))
    keyboard = ReplyKeyboardBuilder()
    async for info in Info.objects.translated(msg.bot.lang).prefetch_related("translations").filter(is_active=True, translations__language_code=msg.bot.lang):
        await sync_to_async(info.set_current_language)(msg.bot.lang)
        keyboard.row(types.KeyboardButton(text=info.title))
    keyboard.row(types.KeyboardButton(text=_(MENU, msg.bot.lang)))
    await msg.answer(_("info_list_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(InfoState.info)


async def info(msg: types.Message, state: FSMContext):
    info = await Info.objects.prefetch_related("translations").filter(translations__title=msg.text).afirst()
    await sync_to_async(info.set_current_language)(msg.bot.lang)
    if not info:
        return msg.answer(_("invalid_info", msg.bot.lang))
    text, file, method = _render_info(info)
    if method == "answer_photo":
        await msg.answer_photo(file, caption=text)
    elif method == "answer":
        await msg.answer(text, disable_web_page_preview=False)


def _render_info(info: Info):
    text = f"""
<strong>{info.title}</strong>

{info.text}
"""
    if info.url:
        text = f"{text}\n{info.url}"
        return text, None, "answer"
    if info.file:
        file = get_file(str(info.file))
        return text, file, "answer_photo"
    return text, None, "answer"


async def accept_url(msg: types.Message):
    await msg.answer(ACCEPT_URL)


async def exit(msg: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text= _(EXIT_CONFIRM, msg.bot.lang), callback_data=EXIT_CONFIRM))
    await msg.answer(_("exit_from_account_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))


async def exit_confirm(cq: types.CallbackQuery, state: FSMContext):
    await ClientId.objects.filter(user_id=cq.from_user.id).aupdate(user=None)
    await menu(cq.message, state)

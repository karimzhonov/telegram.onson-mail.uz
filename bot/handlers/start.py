import os
from django.conf import settings
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.models import User, Info, LANGUAGES, get_text as _
from bot.states import LanguageChooseState
from bot.text_keywords import TAKE_ID, SETTINGS, INFO, LISTID, CHECK, LISTPASSPORT
from users.models import ClientId

async def start(msg: types.Message, state: FSMContext):
    await state.clear()
    if await User.objects.filter(id=msg.from_user.id).aexists():
        return await menu(msg, state)
    await choose_lang(msg, state)


async def menu(msg: types.Message, state: FSMContext):
    await state.clear()
    text = _("menu_text", msg.bot.lang)
    keyboard = ReplyKeyboardBuilder()
    if await ClientId.objects.filter(user_id=msg.from_user.id, deleted=False).aexists():
        keyboard.row(types.KeyboardButton(text=_(LISTID, msg.bot.lang)))
        keyboard.row(types.KeyboardButton(text=_(LISTPASSPORT, msg.bot.lang)))
    else:
        keyboard.row(types.KeyboardButton(text=_(TAKE_ID, msg.bot.lang)))
    keyboard.row(types.KeyboardButton(text=_(SETTINGS, msg.bot.lang)))
    keyboard.row(types.KeyboardButton(text=_(INFO, msg.bot.lang)))
    await msg.answer(text=text, reply_markup=keyboard.as_markup(resize_keyboard=True))


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
    

async def info(msg: types.Message, state: FSMContext):
    if not await Info.objects.filter(is_active=True).aexists():
        return await msg.answer(_("info_not_upload_yeat", msg.bot.lang))
    async for info in Info.objects.translated(msg.bot.lang).filter(is_active=True):
        text = f"""
{_(f'{info.slug}_header', msg.bot.lang)}

{_(f'{info.slug}_desc', msg.bot.lang)}
"""
        file_path = os.path.join(settings.BASE_DIR, "media", str(info.file))
        file = types.BufferedInputFile.from_file(file_path)
        file_suffix = file_path.split(".")[-1].lower()
        if file_suffix in ['jpg', 'jpeg', 'png']:
            await msg.answer_photo(file, text)
        else:
            await msg.answer_video(file, caption=text)
        # await msg.answer_photo(types.BufferedInputFile())

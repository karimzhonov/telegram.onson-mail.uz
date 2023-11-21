import os
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.filters.db_filter import DbSearchFilter
from bot.models import aget_text as _
from bot.states import RegisterState
from bot.text_keywords import MENU, ACCEPT
from users.validators import validate_pnfl, validate_passport, validate_phone
from users.models import Client
from storages.models import Storage
from django.conf import settings
from django.core.exceptions import ValidationError


async def take_id(msg: types.Message, state: FSMContext):
    text = await _("enter_pnfl_text", msg.bot.lang)
    
    await msg.answer_photo(
        types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "bot/static/images/passport.jpg")), 
        text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegisterState.pnfl)


async def entered_pnfl(msg: types.Message, state: FSMContext):
    try:
        value = validate_pnfl(msg.text)
    except ValidationError as _exp:
        await msg.answer(await _(_exp.message, msg.bot.lang, pnfl=msg.text))
    else:
        await state.update_data(pnfl=value)
        if await Client.objects.filter(pnfl=value).aexists():
            return await client_render(msg, state)
        await enter_fio(msg, state)


async def enter_fio(msg: types.Message, state: FSMContext):
    text = await _("enter_fio_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.fio)


async def entered_fio(msg: types.Message, state: FSMContext):
    await state.update_data(fio=msg.text)
    await enter_passport(msg, state)


async def enter_passport(msg: types.Message, state: FSMContext):
    text = await _("enter_passport_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.passport)


async def entered_passport(msg: types.Message, state: FSMContext):
    try:
        value = validate_passport(msg.text)
    except ValidationError as _exp:
        await msg.answer(await _(_exp.message, msg.bot.lang, pnfl=msg.text))
    else:
        await state.update_data(passport=value)
        await enter_phone(msg, state)


async def enter_phone(msg: types.Message, state: FSMContext):
    text = await _("enter_phone_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.phone)


async def entered_phone(msg: types.Message, state: FSMContext):
    try:
        value = validate_phone(msg.text)
    except ValidationError as _exp:
        await msg.answer(await _(_exp.message, msg.bot.lang, pnfl=msg.text))
    else:
        await state.update_data(phone=value)
        # await client_created(msg, state)
        await msg.answer(await _("accept-creating", msg.bot.lang))
        await msg.answer('url', reply_markup=ReplyKeyboardBuilder([[types.KeyboardButton(text= await _(ACCEPT, msg.bot.lang))]]).as_markup(resize_keyboard=True))
        await state.set_state(RegisterState.accept)

async def accepted_creating(msg: types.Message, state: FSMContext):
    if (await DbSearchFilter(ACCEPT)(msg, msg.bot)):
        return await client_created(msg, state)
    await msg.answer(await _('error_accept_creating', msg.bot.lang))



async def client_created(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await Client.objects.acreate(
        pnfl=data["pnfl"],
        fio=data['fio'],
        phone=data['phone'],
        passport=data['passport']
    )
    await msg.answer(await _('client_created', msg.bot.lang))
    await client_render(msg, state)    


async def entered_storage(msg: types.Message, state: FSMContext):
    if (await DbSearchFilter(MENU)(msg, msg.bot)):
        from .start import start
        return await start(msg, state)
    try:
        data = await state.get_data()
        storage = await Storage.objects.aget(name=msg.text)
        client = await Client.objects.aget(pnfl=data['pnfl'])
    except (Storage.DoesNotExist, Client.DoesNotExist):
        await msg.answer(await _("invalid_storage", msg.bot.lang))
    else:
        id = f"{storage.slug}-{client.id}"
        text = f"""
{await _('storage_name', msg.bot.lang)}: {storage.name}
{await _('storage_address', msg.bot.lang)}: {storage.address}

{await _('client', msg.bot.lang)}: {client.fio}
ID: {id}
"""
        await msg.answer(text)


async def client_render(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    client = await Client.objects.aget(pnfl=data['pnfl'])
    text = f"""
{await _('client_info', msg.bot.lang)}
{await _('fio', msg.bot.lang)}: {client.fio}
{await _('passport', msg.bot.lang)}: {client.passport}
{await _('pnfl', msg.bot.lang)}: {client.pnfl}
{await _('phone', msg.bot.lang)}: {client.phone}

{await _('select_storage_for_id', msg.bot.lang)}
"""
    keyboard = ReplyKeyboardBuilder(
        [[types.KeyboardButton(text=storage.name)] async for storage in Storage.objects.filter(is_active=True)]
    )
    keyboard.row(types.KeyboardButton(text=await _(MENU, msg.bot.lang)))

    await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(RegisterState.storage)

    
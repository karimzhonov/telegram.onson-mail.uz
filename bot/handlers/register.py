import os, io
from aiogram import Dispatcher, F
from aiogram.types import ContentType as CT
from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.filters.db_filter import DbSearchFilter
from bot.models import get_text as _
from bot.states import RegisterState
from bot.text_keywords import TAKE_ID, ACCEPT, ID_PASSPORT, BIO_PASSPORT
from bot.utils import concat_images
from users.validators import validate_pnfl, validate_passport, validate_phone
from users.models import Client, ClientId
from storages.models import Storage
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image

def setup(dp: Dispatcher): 
    dp.message(DbSearchFilter(TAKE_ID))(take_id)
    dp.message(RegisterState.pnfl)(entered_pnfl)
    dp.message(RegisterState.fio)(entered_fio)
    dp.message(RegisterState.passport)(entered_passport)
    dp.message(RegisterState.is_id_passport)(entered_passport_type)
    dp.message(RegisterState.passport_image, F.content_type.in_([CT.PHOTO]))(entered_passport_image)
    dp.message(RegisterState.city)(entered_city)
    dp.message(RegisterState.region)(entered_region)
    dp.message(RegisterState.phone)(entered_phone)
    dp.message(RegisterState.accept)(accepted_creating)


async def take_id(msg: types.Message, state: FSMContext):
    text = _("enter_pnfl_text", msg.bot.lang)
    await msg.answer_photo(
        types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "bot/assets/images/passport.jpg")), 
        text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RegisterState.pnfl)


async def entered_pnfl(msg: types.Message, state: FSMContext):
    try:
        value = await validate_pnfl(msg.text)
    except ValidationError as _exp:
        await msg.answer(_(_exp.message, msg.bot.lang, pnfl=msg.text))
    else:
        await state.update_data(pnfl=value)
        if await Client.objects.filter(pnfl=value).aexists():
            return await client_render(msg, state)
        await enter_fio(msg, state)


async def enter_fio(msg: types.Message, state: FSMContext):
    text = _("enter_fio_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.fio)


async def entered_fio(msg: types.Message, state: FSMContext):
    await state.update_data(fio=msg.text)
    await enter_passport(msg, state)


async def enter_passport(msg: types.Message, state: FSMContext):
    text = _("enter_passport_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.passport)


async def entered_passport(msg: types.Message, state: FSMContext):
    try:
        value = await validate_passport(msg.text)
    except ValidationError as _exp:
        await msg.answer(_(_exp.message, msg.bot.lang, pnfl=msg.text))
    else:
        await state.update_data(passport=value)
        await enter_passport_type(msg, state)


async def enter_passport_type(msg: types.Message, state: FSMContext):
    text = _("enter_passport_type_text", msg.bot.lang)
    keyboard = ReplyKeyboardBuilder([[types.KeyboardButton(text= _(ID_PASSPORT, msg.bot.lang))], [types.KeyboardButton(text= _(BIO_PASSPORT, msg.bot.lang))]])
    await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(RegisterState.is_id_passport)


async def entered_passport_type(msg: types.Message, state: FSMContext):
    if await DbSearchFilter(ID_PASSPORT)(msg, msg.bot):
        await state.update_data(is_id_passport=True, passport_image=[])
    elif await DbSearchFilter(BIO_PASSPORT)(msg, msg.bot):
        await state.update_data(is_id_passport=False, passport_image=[])
    else:
        return await msg.answer(_("error_passport_type", msg.bot.lang))
    await enter_passport_image(msg, state)


async def enter_passport_image(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if data["is_id_passport"] and len(data["passport_image"]) == 0:
        await msg.answer_photo(
            types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "bot/assets/images/id_passport_front.jpg")), 
            _("enter_id_passport_image_front", msg.bot.lang), reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegisterState.passport_image)
    elif data["is_id_passport"] and len(data["passport_image"]) == 1:
        await msg.answer_photo(
            types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "bot/assets/images/id_passport_back.jpg")), 
            _("enter_id_passport_image_back", msg.bot.lang), reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegisterState.passport_image)
    elif data["is_id_passport"] and len(data["passport_image"]) == 2:
        await enter_city(msg, state)
    elif not data["is_id_passport"] and len(data["passport_image"]) == 0:
        await msg.answer_photo(
            types.BufferedInputFile.from_file(os.path.join(settings.BASE_DIR, "bot/assets/images/bio_passport.png")), 
            _("enter_bio_passport_image", msg.bot.lang), reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegisterState.passport_image)
    elif not data["is_id_passport"] and len(data["passport_image"]) == 1:
        await enter_city(msg, state)


async def entered_passport_image(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    data["passport_image"].append(msg.photo[-1].file_id)
    await state.update_data(passport_image=data["passport_image"])
    await enter_passport_image(msg, state)


async def enter_city(msg: types.Message, state: FSMContext):
    text = _("enter_city_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.city)


async def entered_city(msg: types.Message, state: FSMContext):
    await state.update_data(city=msg.text)
    await enter_region(msg, state)


async def enter_region(msg: types.Message, state: FSMContext):
    text = _("enter_region_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.region)


async def entered_region(msg: types.Message, state: FSMContext):
    await state.update_data(region=msg.text)
    await enter_phone(msg, state)


async def enter_phone(msg: types.Message, state: FSMContext):
    text = _("enter_phone_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.phone)


async def entered_phone(msg: types.Message, state: FSMContext):
    try:
        value = await validate_phone(msg.text)
    except ValidationError as _exp:
        await msg.answer(_(_exp.message, msg.bot.lang, pnfl=msg.text))
    else:
        await state.update_data(phone=value)
        # await client_created(msg, state)
        await msg.answer(_("accept-creating", msg.bot.lang))
        await msg.answer('https://teletype.in/@khtkarimzhonov/shartnoma', reply_markup=ReplyKeyboardBuilder([[types.KeyboardButton(text= _(ACCEPT, msg.bot.lang))]]).as_markup(resize_keyboard=True))
        await state.set_state(RegisterState.accept)

async def accepted_creating(msg: types.Message, state: FSMContext):
    if (await DbSearchFilter(ACCEPT)(msg, msg.bot)):
        return await client_created(msg, state)
    await msg.answer(_('error_accept_creating', msg.bot.lang))


async def client_created(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    images = []
    for image_id in data["passport_image"]:
        file: io.BytesIO = await msg.bot.download(image_id)
        image = Image.open(file)
        images.append(image)
    
    image = concat_images(images)
    with io.BytesIO() as file:
        image.save(file, "PNG")

        client = await Client.objects.acreate(
            pnfl=data["pnfl"],
            fio=data['fio'],
            phone=data['phone'],
            passport=data['passport'],
            address=", ".join([data["city"], data['region']])
        )
        await client.save_passport_image(ContentFile(file.getvalue()))
        await _client_to_clientid(msg, state, client)
        await msg.answer(_('client_created', msg.bot.lang))
        await client_render(msg, state)    


async def _client_to_clientid(msg: types.Message, state: FSMContext, client: Client):
    data = await state.get_data()
    if data.get("client_id"):
        client_id = await ClientId.objects.select_related("storage", "selected_client").aget(id=data.get("client_id"))
        await client_id.aadd_client(client)
    else:
        async for storage in Storage.objects.translated(msg.bot.lang).all():
            client_id, created = await ClientId.objects.aget_or_create({
                "storage": storage,
                "selected_client": client
            }, storage=storage, selected_client=client
            )
            if created:
                await ClientId.objects.filter(id=client_id.id).aupdate(id_str=client_id.get_id())
            if not client_id.user_id == msg.from_user.id:
                await ClientId.objects.filter(id=client_id.id).aupdate(user_id=msg.from_user.id)
            if not await client_id.clients.filter(id=client.id).aexists():
                await client_id.aadd_client(client)


async def client_render(msg: types.Message, state: FSMContext):
    from .storages import storage_list

    data = await state.get_data()
    client = await Client.objects.aget(pnfl=data['pnfl'])
    text = f"""
{_('client_info', msg.bot.lang)}
{_('fio', msg.bot.lang)}: {client.fio}
{_('passport', msg.bot.lang)}: {client.passport}
{_('pnfl', msg.bot.lang)}: {client.pnfl}
{_('phone', msg.bot.lang)}: {client.phone}
{_('address', msg.bot.lang)}: {client.address}
"""
    await _client_to_clientid(msg, state, client)
    await msg.answer(text)
    await storage_list(msg, state)

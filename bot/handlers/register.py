import os, io
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.filters.db_filter import DbSearchFilter
from bot.models import get_text as _
from bot.states import RegisterState
from bot.text_keywords import MENU, ACCEPT
from users.validators import validate_pnfl, validate_passport, validate_phone
from users.models import Client, ClientId
from storages.models import Storage
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Q

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
        await enter_passport_image(msg, state)


async def enter_passport_image(msg: types.Message, state: FSMContext):
    text = _("enter_passport_image_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(RegisterState.passport_image)


async def entered_passport_image(msg: types.Message, state: FSMContext):
    await state.update_data(passport_image=msg.photo[-1].file_id)
    await enter_city(msg, state)


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
    file: io.BytesIO = await msg.bot.download(data["passport_image"])

    client = await Client.objects.acreate(
        pnfl=data["pnfl"],
        fio=data['fio'],
        phone=data['phone'],
        passport=data['passport'],
        address=", ".join([data["city"], data['region']])
    )
    await client.save_passport_image(ContentFile(file.getvalue()))
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
            if not client_id.user_id == msg.from_user.id:
                await ClientId.objects.filter(id=client_id.id).aupdate(user_id=msg.from_user.id)
            if not await client_id.clients.filter(id=client.id).aexists():
                await client_id.aadd_client(client)
    await msg.answer(_('client_created', msg.bot.lang))
    await client_render(msg, state)    


async def entered_storage(msg: types.Message, state: FSMContext):
    if (await DbSearchFilter(MENU)(msg, msg.bot)):
        from .start import start
        return await start(msg, state)
    try:
        data = await state.get_data()
        storage = await Storage.objects.prefetch_related("translations").aget(translations__name=msg.text, translations__language_code=msg.bot.lang)
        client = await Client.objects.aget(pnfl=data['pnfl'])
        if data.get("client_id"):
            if await ClientId.objects.filter(~Q(id=data.get("client_id")) & ~Q(user_id=msg.from_user.id), selected_client=client, deleted=False, storage=storage).aexists():
                client_id = await ClientId.objects.filter(~Q(id=data.get("client_id")), selected_client=client, deleted=False, storage=storage).afirst()
                if await client_id.clients.acount() > 1:
                    await client_id.aremove_client(client)
                    await ClientId.objects.filter(~Q(id=data.get("client_id")), selected_client=client, deleted=False, storage=storage).aupdate(selected_client=await client_id.clients.afirst())
                else:
                    await ClientId.objects.filter(~Q(id=data.get("client_id")), selected_client=client, deleted=False, storage=storage).aupdate(deleted=True, selected_client=None)
                    await client_id.aremove_client(client)
            client_id = await ClientId.objects.select_related("storage", "selected_client").aget(id=data.get("client_id"))
            await client_id.aadd_client(client)
            await ClientId.objects.filter(id=data.get("client_id")).aupdate(selected_client=client)
        else:
            try:
                if await ClientId.objects.filter(~Q(user_id=msg.from_user.id), clients__in=[client], deleted=False, storage=storage).aexists():
                    client_id = await ClientId.objects.filter(selected_client=client, deleted=False, storage=storage).afirst()
                    if await client_id.clients.acount() > 1:
                        await client_id.aremove_client(client)
                        await ClientId.objects.filter(selected_client=client, deleted=False, storage=storage).aupdate(selected_client=await client_id.clients.afirst())
                    else:
                        await ClientId.objects.filter(selected_client=client, deleted=False, storage=storage).aupdate(deleted=True, selected_client=None)
                        await client_id.aremove_client(client)
                client_id = await ClientId.objects.select_related("storage", "selected_client").aget(clients__in=[client], storage=storage, deleted=False)              
            except ClientId.DoesNotExist:
                client_id, created = await ClientId.objects.aget_or_create({"storage": storage, "selected_client": client}, 
                                                                           storage=storage, selected_client=client)
            if not client_id.user_id == msg.from_user.id:
                await ClientId.objects.filter(id=client_id.id).aupdate(user_id=msg.from_user.id)
            if client_id.deleted:
                await ClientId.objects.filter(id=client_id.id).aupdate(deleted=False)
            if not await client_id.clients.filter(id=client.id).aexists():
                await client_id.aadd_client(client)
    except (Storage.DoesNotExist, Client.DoesNotExist):
        await msg.answer(_("invalid_storage", msg.bot.lang))
    else:
        id = client_id.get_id()
        text = f"""
{_('storage_name', msg.bot.lang)}: {storage.name}
{_('storage_phone', msg.bot.lang)}: {storage.phone}
{_('storage_address', msg.bot.lang)}: <code>{storage.address}</code>
{storage.text}
{_('client', msg.bot.lang)}: {client.fio}
ID: <code>{id}</code>
"""
        await msg.answer(text)


async def client_render(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    client = await Client.objects.aget(pnfl=data['pnfl'])
    text = f"""
{_('client_info', msg.bot.lang)}
{_('fio', msg.bot.lang)}: {client.fio}
{_('passport', msg.bot.lang)}: {client.passport}
{_('pnfl', msg.bot.lang)}: {client.pnfl}
{_('phone', msg.bot.lang)}: {client.phone}
{_('address', msg.bot.lang)}: {client.address}

{_('select_storage_for_id', msg.bot.lang)}
"""
    keyboard = ReplyKeyboardBuilder(
        [[types.KeyboardButton(text=storage.name)] async for storage in Storage.objects.translated(msg.bot.lang).filter(is_active=True)]
    )
    keyboard.row(types.KeyboardButton(text=_(MENU, msg.bot.lang)))

    await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(RegisterState.storage)

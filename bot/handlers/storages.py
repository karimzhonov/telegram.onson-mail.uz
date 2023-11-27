from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from bot.filters.db_filter import DbSearchFilter
from bot.models import get_text as _
from bot.states import IDStorage
from bot.text_keywords import MENU, STORAGES, CHECK, WARINNG
from storages.models import Storage
from users.models import ClientId


def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(STORAGES))(storage_list)
    dp.message(IDStorage.storage)(storage_info)
    dp.callback_query(IDStorage.passport)(selected_passport)



async def storage_list(msg: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardBuilder()
    if not await Storage.objects.translated(msg.bot.lang).filter(is_active=True).aexists():
        return await msg.answer(_("storage_list_empty", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    async for storage in Storage.objects.prefetch_related("translations").translated(msg.bot.lang).filter(is_active=True):
        keyboard.row(types.KeyboardButton(text=storage.name))
    keyboard.row(types.KeyboardButton(text=_(MENU, msg.bot.lang)))
    await msg.answer(_("storage_list_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(IDStorage.storage)


async def storage_info(msg: types.Message, state: FSMContext):
    try:
        storage = await Storage.objects.prefetch_related("translations").aget(translations__name=msg.text, translations__language_code=msg.bot.lang)
        await _render_storage(msg.from_user.id, msg, state, storage)
        await state.set_state(IDStorage.passport)
    except Storage.DoesNotExist:
        await msg.answer(_("invalid_storage", msg.bot.lang))



async def _render_storage(user_id, msg: types.Message, state: FSMContext, storage, edit=False, passport=True):
    main_text = f"""
{_('storage_name', msg.bot.lang)}: {storage.name}
{_('storage_phone', msg.bot.lang)}: {storage.phone}
{_('storage_price', msg.bot.lang)}: {storage.per_price} $
{storage.text}
"""
    storage_address_text = f"""
{_('storage_address', msg.bot.lang)}: <code>{storage.address}</code>
<i>{_('storage_address_copy', msg.bot.lang)}</i>
"""
    client_text = ""
    keyboard = InlineKeyboardBuilder()
    if await ClientId.objects.filter(user_id=user_id).aexists():
        client_id, created = await ClientId.objects.select_related("storage", "selected_client").prefetch_related("clients", "storage__translations").aget_or_create(user_id=user_id, deleted=False, storage=storage)
        async for client in client_id.clients.all():
            text = []
            if client.id == client_id.selected_client_id:
                text.append(CHECK)
            is_warning = await client.ais_warning()
            if is_warning:
                text.append(WARINNG)
            text.append(str(client.fio))
            text.append(f"({client.passport})")
            if is_warning:
                text.append(WARINNG)
            keyboard.row(types.InlineKeyboardButton(text= " ".join(text), callback_data=f"{client_id.id}:{client.id}"))
        keyboard.row(types.InlineKeyboardButton(text=_("add_passport", msg.bot.lang), callback_data=f"{client_id.id}:add_passport"))
        client_text = f"""
{_('client_id', msg.bot.lang)}: <code>{client_id.get_id()}</code> <i>{_('client_id_copy', msg.bot.lang)}</i>

{WARINNG} {_('client_warning_quater_limit', msg.bot.lang)} {WARINNG}
"""
        storage_address_text = f"""
{_('storage_address', msg.bot.lang)}: <code>{storage.address}, {client_id.get_id()}</code>
<i>{_('storage_address_copy', msg.bot.lang)}</i>
"""
        main_text = f"{main_text}\n{storage_address_text}\n{client_text}"
    if not edit:
        await msg.answer(main_text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        await msg.edit_text(main_text, reply_markup=keyboard.as_markup(resize_keyboard=True))


async def selected_passport(cq: types.CallbackQuery, state: FSMContext):
    if "add_passport" in cq.data.split(":"):
        from .register import take_id
        await state.clear()
        client_id = await ClientId.objects.select_related("storage", "selected_client").prefetch_related("clients").aget(id=cq.data.split(":")[0])
        await state.update_data(client_id=client_id.id)
        return await take_id(cq.message, state)
    client = int(cq.data.split(":")[1])
    client_id = await ClientId.objects.select_related("storage", "selected_client").prefetch_related("clients").aget(id=cq.data.split(":")[0])
    if client_id.selected_client_id == client:
        return
    await ClientId.objects.filter(id=client_id.id).aupdate(selected_client_id=client)
    await _render_storage(cq.from_user.id, cq.message, state, client_id.storage, edit=True)

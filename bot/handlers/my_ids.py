from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from users.models import ClientId
from bot.text_keywords import MENU, CHECK
from bot.models import get_text as _
from bot.states import ListId
from storages.models import Storage

async def my_ids(msg: types.Message, state: FSMContext):
    await _render_ids(msg, state=state)
    await state.set_state(ListId.passport)


async def _render_ids(msg: types.Message, edit=False, state=None):
    async for storage in Storage.objects.filter(is_active=True):
        await _render_id(msg.from_user.id, msg, state, storage, edit)  


async def _render_id(user_id, msg: types.Message, state: FSMContext, storage, edit=False):
    client_id, created = await ClientId.objects.select_related("storage", "selected_client").prefetch_related("clients").aget_or_create(user_id=user_id, deleted=False, storage=storage)
    keyboard = InlineKeyboardBuilder()
    async for client in client_id.clients.all():
        text = []
        if client.id == client_id.selected_client_id:
            text.append(CHECK)
        text.append(str(client.fio))
        text.append(f"({client.passport})")
        keyboard.row(types.InlineKeyboardButton(text= " ".join(text), callback_data=f"{client_id.id}:{client.id}"))
    keyboard.row(types.InlineKeyboardButton(text=_("add_passport", msg.bot.lang), callback_data=f"{client_id.id}:add_passport"))
    text = f"""
{_('storage_name', msg.bot.lang)}: {client_id.storage.name}
{_('storage_address', msg.bot.lang)}: <code>{client_id.storage.address}</code>

ID: <code>{client_id.get_id()}</code>
"""
    if not edit:
        await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        await msg.edit_text(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


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
    await _render_id(cq.from_user.id, cq.message, state, client_id.storage, edit=True)

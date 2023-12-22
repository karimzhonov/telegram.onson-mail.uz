from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from asgiref.sync import sync_to_async

from bot.filters.db_filter import DbSearchFilter
from bot.models import get_text as _
from bot.states import OnlineBuy
from bot.text_keywords import (MENU, ONLINE_BUY, ONLINE_BUY_ABOUT, ONLINE_BUY_CART, ONLINE_BUY_CATEGORY,
                               ONLINE_BUY_CHOSEN, ONLINE_BUY_MENU, ONLINE_BUY_ORDERS)
from orders.models import Order
from storages.models import Product, ProductToCart, ProductToChosen, Storage
from users.models import ClientId

from . import cart, category, chosens, orders


def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(ONLINE_BUY))(storage_list)
    dp.message(OnlineBuy.storage)(storage_menu)
    dp.message(DbSearchFilter(ONLINE_BUY_MENU))(storage_menu_back)
    dp.message(DbSearchFilter(ONLINE_BUY_ABOUT))(about)
    cart.setup(dp)
    chosens.setup(dp)
    category.setup(dp)
    orders.setup(dp)


async def storage_list(msg: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardBuilder()
    if not await Storage.objects.translated(msg.bot.lang).filter(has_online_buy=True).aexists():
        return await msg.answer(_("storage_list_empty", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    async for storage in Storage.objects.prefetch_related("translations").translated(msg.bot.lang).filter(has_online_buy=True):
        await sync_to_async(storage.set_current_language)(msg.bot.lang)
        keyboard.row(types.KeyboardButton(text=storage.name))
    keyboard.row(types.KeyboardButton(text=_(MENU, msg.bot.lang)))
    await msg.answer(_("online_buy_storage_list_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(OnlineBuy.storage)


async def storage_menu(msg: types.Message, state: FSMContext):
    try:
        storage = await Storage.objects.prefetch_related("translations").aget(translations__name=msg.text, translations__language_code=msg.bot.lang, has_online_buy=True)
        await state.update_data(storage=storage.id)
        await _render_storage_menu(msg, state)
        await state.set_state(OnlineBuy.menu)
    except Storage.DoesNotExist:
        await msg.answer(_("invalid_storage", msg.bot.lang))


async def storage_menu_back(msg: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        storage = await Storage.objects.prefetch_related("translations").aget(id=data.get("storage"))
        await state.update_data(storage=storage.id, category=None)
        await _render_storage_menu(msg, state)
        await state.set_state(OnlineBuy.menu)
    except Storage.DoesNotExist:
        await msg.answer(_("invalid_storage", msg.bot.lang))


async def _render_storage_menu(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    clientid = await ClientId.objects.filter(storage_id=data["storage"], user_id=msg.from_user.id).select_related("storage").afirst()
    keyboard = [
        [types.KeyboardButton(text=f"{_(ONLINE_BUY_CATEGORY, msg.bot.lang)} ({await Product.objects.filter(storage_id=data['storage']).acount()})")],        
    ]
    if clientid:
        keyboard.append(
            [types.KeyboardButton(text=f"{_(ONLINE_BUY_CHOSEN, msg.bot.lang)} ({await ProductToChosen.objects.filter(clientid=clientid).acount()})")],
        )
        keyboard.append(
            [types.KeyboardButton(text=f"{_(ONLINE_BUY_CART, msg.bot.lang)} ({await ProductToCart.objects.filter(cart__clientid=clientid).acount()})")],
        )
        keyboard.append(
            [types.KeyboardButton(text=f"{_(ONLINE_BUY_ORDERS, msg.bot.lang)} ({await Order.objects.filter(part__storage_id=data['storage'], client__clientid__user_id=clientid.user_id, with_online_buy=True).acount()})")],
        )
    else:
        keyboard.append(
            [types.KeyboardButton(text=f"{_(ONLINE_BUY_CHOSEN, msg.bot.lang)}")],
        )
        keyboard.append(
            [types.KeyboardButton(text=f"{_(ONLINE_BUY_CART, msg.bot.lang)}")],
        )
        keyboard.append(
            [types.KeyboardButton(text=f"{_(ONLINE_BUY_ORDERS, msg.bot.lang)}")],
        )
       
    keyboard.append(
        [types.KeyboardButton(text=_(ONLINE_BUY_ABOUT, msg.bot.lang))]
    )
    keyboard.append(
        [types.KeyboardButton(text=_(ONLINE_BUY, msg.bot.lang))]
    )
    keyboard = ReplyKeyboardBuilder(keyboard)
    await msg.answer(_("online_by_menu", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))


async def about(msg: types.Message, state: FSMContext):
    from bot.handlers.storages import _render_storage

    try:
        data = await state.get_data()
        storage = await Storage.objects.prefetch_related("translations").aget(id=data["storage"], translations__language_code=msg.bot.lang)
        await _render_storage(msg.from_user.id, msg, state, storage, passport=False)
    except Storage.DoesNotExist:
        await msg.answer(_("invalid_storage", msg.bot.lang))


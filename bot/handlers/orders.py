from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.filters.db_filter import DbSearchFilter
from bot.filters.prefix import Prefix
from bot.models import get_text as _
from bot.text_keywords import ORDERS
from orders.models import Order
from users.models import ClientId
from .online_buy.orders import _render_order

LIMIT = 5

def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(ORDERS))(my_orders)
    dp.callback_query(Prefix("main_order"))(report_action)


async def my_orders(msg: types.Message, state: FSMContext, offset=0, user_id=None):
    user_id = msg.from_user.id if not user_id else user_id
    clientid = await ClientId.objects.filter(user_id=user_id).select_related("user", "storage").afirst()
    if not clientid:
        return await msg.answer(_("product_list_empty", msg.bot.lang))
    orders = Order.objects.filter(with_online_buy=False, client__in=clientid.clients.all())
    if not await orders.aexists():
        return await msg.answer(_("product_list_empty", msg.bot.lang))
    orders = orders.select_related("client", "part", "part__storage").order_by("-date")
    async for order in orders[offset:offset + LIMIT]:
        text = await _render_order(clientid.user, order)
        await msg.answer(text)

    products_count = await orders.acount()
    text = f"""{_("showed_offset_orders_in_count", msg.bot.lang, offset=LIMIT + offset, count=products_count)}"""
    keyboard = InlineKeyboardBuilder()
    if LIMIT + offset < products_count:
        keyboard.row(types.InlineKeyboardButton(text=_("show_again", msg.bot.lang), callback_data=f"main_order:show_again:{offset + LIMIT}"))
        await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


async def report_action(cq: types.CallbackQuery, state: FSMContext):
    msg = cq.message
    type, *cq_data_list = cq.data.split(":")
    if cq_data_list[0] == "show_again":
        await msg.delete()
        await my_orders(msg, state, int(cq_data_list[1]), cq.from_user.id)

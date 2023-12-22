from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import async_to_sync

from bot.filters.db_filter import DbSearchFilter
from bot.filters.prefix import Prefix
from bot.models import get_text as _
from bot.text_keywords import ONLINE_BUY_ORDERS, WARINNG
from orders.models import Order
from users.models import ClientId

LIMIT = 5

def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(ONLINE_BUY_ORDERS))(my_orders)
    dp.callback_query(Prefix("order"))(report_action)


async def my_orders(msg: types.Message, state: FSMContext, offset=0, user_id=None):
    user_id = msg.from_user.id if not user_id else user_id
    data = await state.get_data()
    clientid = await ClientId.objects.filter(storage_id=data["storage"], user_id=user_id).select_related("user", "storage").afirst()
    if not clientid:
        return await msg.answer(_("product_list_empty", msg.bot.lang))
    orders = Order.objects.filter(part__storage_id=data["storage"], with_online_buy=True, client__in=clientid.clients.all())
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
        keyboard.row(types.InlineKeyboardButton(text=_("show_again", msg.bot.lang), callback_data=f"order:show_again:{offset + LIMIT}"))
        await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


async def _render_order(user, order: Order, limit=False):
    text = f"""
{_('part', user.lang)}: {order.part.number}
{_('order_number', user.lang)}: {order.number}
{_('client_id', user.lang)}: {order.clientid}
{_('client', user.lang)}: {order.client}
{_('passport', user.lang)}: {order.client.passport}
{_('order_name', user.lang)}: {order.name}
{_('order_weight', user.lang)}: {order.weight} {_('kg', user.lang)}
{_('order_facture_price', user.lang)}: {order.facture_price} $
{_('order_price', user.lang)}: {order.payed_price} $
{_('order_status', user.lang)}: {_(f'order_status_{order.part.status}', user.lang)}
"""
    if limit:
        current_quarter = await order.client.order_quarters().order_by("quarter").alast()
        current_quarter = 0 if not current_quarter else current_quarter['value']
        text = f"""{text}
{WARINNG} {_('current_quarter', user.lang)}: {current_quarter} $ {WARINNG}
"""
    return text


async def report_action(cq: types.CallbackQuery, state: FSMContext):
    msg = cq.message
    type, *cq_data_list = cq.data.split(":")
    if cq_data_list[0] == "show_again":
        await msg.delete()
        await my_orders(msg, state, int(cq_data_list[1]), cq.from_user.id)

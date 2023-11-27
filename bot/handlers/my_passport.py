from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from users.models import Client
from bot.text_keywords import WARINNG, LISTPASSPORT
from bot.models import get_text as _
from bot.states import ListPassport
from bot.filters.db_filter import DbSearchFilter


def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(LISTPASSPORT))(my_passports)
    dp.callback_query(ListPassport.passport)(select_passport)


async def my_passports(msg: types.Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardBuilder()
    async for client in Client.objects.filter(clientid__user_id=msg.from_user.id).distinct("id"):
        text = []
        is_warning = await client.ais_warning()
        if is_warning:
            text.append(WARINNG)
        text.append(str(client.fio))
        text.append(f"({client.passport})")
        if is_warning:
            text.append(WARINNG)
        keyboard.row(types.InlineKeyboardButton(text= " ".join(text), callback_data=f"{client.id}"))
    text = f"""
{_("my_passports_text", msg.bot.lang)}

{WARINNG} {_('client_warning_quater_limit', msg.bot.lang)} {WARINNG}
    """
    await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(ListPassport.passport)


async def select_passport(cq: types.CallbackQuery, state: FSMContext):
    msg = cq.message
    client = int(cq.data)
    client = await Client.objects.aget(id=client)
    current_quarter = await client.order_quarters().order_by("quarter").alast()
    current_quarter = 0 if not current_quarter else current_quarter['value']
    
    table = ["|------------------|------------------|", f"|{_('quarter', msg.bot.lang).center(18)}|{_('limit', msg.bot.lang).center(18)}|", "|------------------|------------------|"]
    summa = 0
    async for quarter in client.order_quarters().order_by("-quarter"):
        summa += quarter["value"]
        date = str(quarter["quarter"]).center(18)
        limit = str(quarter["value"]).center(18)
        table.append(f"|{date}|{limit}|")
    table.append("|------------------|------------------|")
    table.append(f"|{_('summa', msg.bot.lang).center(18)}|{str(summa).center(18)}|")
    table.append("|------------------|------------------|")
    table = "\n".join(table)
    text = f"""
{_('client_info', msg.bot.lang)}
{_('fio', msg.bot.lang)}: {client.fio}
{_('passport', msg.bot.lang)}: {client.passport}
{_('pnfl', msg.bot.lang)}: {client.pnfl}
{_('phone', msg.bot.lang)}: {client.phone}
{_('address', msg.bot.lang)}: {client.address}
{_('current_quarter', msg.bot.lang)}: {current_quarter} $

<pre>
{table}
</pre>
"""
    await msg.answer(text)

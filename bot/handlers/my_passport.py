from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.exceptions import ValidationError
from users.models import Client
from users.validators import validate_phone
from bot.text_keywords import WARINNG, LISTPASSPORT, MENU
from bot.models import get_text as _
from bot.states import ListPassport
from bot.filters.db_filter import DbSearchFilter
from bot.filters.prefix import Prefix


CHANGE_PHONE = "change_phone"
CHANGE_ADRESS = "change_adress"


def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(LISTPASSPORT))(my_passports)
    dp.callback_query(ListPassport.action, Prefix(CHANGE_PHONE))(change_phone)
    dp.callback_query(ListPassport.action, Prefix(CHANGE_ADRESS))(change_adress)
    dp.callback_query(ListPassport.passport)(select_passport)
    dp.message(ListPassport.phone)(entered_phone)
    dp.message(ListPassport.city)(entered_city)
    dp.message(ListPassport.region)(entered_region)


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
    await state.update_data(passport=client)
    client = await Client.objects.aget(id=client)
    await _render_passport_with_keyboard(client, msg)
    await state.set_state(ListPassport.action)


async def _render_passport_with_keyboard(client: Client, msg: types.Message):
    keyboard = InlineKeyboardBuilder()
    text = await _render_passport(client, msg.bot.lang)
    keyboard.row(types.InlineKeyboardButton(text=_(CHANGE_PHONE, msg.bot.lang), callback_data=CHANGE_PHONE))
    keyboard.row(types.InlineKeyboardButton(text=_(CHANGE_ADRESS, msg.bot.lang), callback_data=CHANGE_ADRESS))
    await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


async def _render_passport(client: Client, lang):
    current_quarter = await client.order_quarters().order_by("quarter").alast()
    current_quarter = 0 if not current_quarter else current_quarter['value']
    
    table = ["|------------------|------------------|", f"|{_('quarter', lang).center(18)}|{_('limit', lang).center(18)}|", "|------------------|------------------|"]
    summa = 0
    async for quarter in client.order_quarters().order_by("-quarter"):
        summa += quarter["value"]
        date = str(quarter["quarter"]).center(18)
        limit = str(quarter["value"]).center(18)
        table.append(f"|{date}|{limit}|")
    table.append("|------------------|------------------|")
    table.append(f"|{_('summa', lang).center(18)}|{str(summa).center(18)}|")
    table.append("|------------------|------------------|")
    table = "\n".join(table)
    text = f"""
{_('client_info', lang)}
{_('fio', lang)}: {client.fio}
{_('passport', lang)}: {client.passport}
{_('pnfl', lang)}: {client.pnfl}
{_('phone', lang)}: {client.phone}
{_('address', lang)}: {client.address}
{_('current_quarter', lang)}: {current_quarter} $

<pre>
{table}
</pre>
"""
    if await client.ais_warning():
        warnign_text = f'{WARINNG} {_("client_passport_warning_quater_limit", lang)} {WARINNG}'    
        text = f"{text}\n{warnign_text}"
    return text


async def change_phone(cq: types.CallbackQuery, state: FSMContext):
    await enter_phone(cq.message, state)


async def change_adress(cq: types.CallbackQuery, state: FSMContext):
    await enter_city(cq.message, state)


async def enter_city(msg: types.Message, state: FSMContext):
    text = _("enter_city_text", msg.bot.lang)
    await msg.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()
    await state.set_state(ListPassport.city)


async def entered_city(msg: types.Message, state: FSMContext):
    await state.update_data(city=msg.text)
    await enter_region(msg, state)


async def enter_region(msg: types.Message, state: FSMContext):
    text = _("enter_region_text", msg.bot.lang)
    await msg.answer(text)
    await state.set_state(ListPassport.region)


async def entered_region(msg: types.Message, state: FSMContext):
    from .start import _menu_keyboard
    await state.update_data(region=msg.text)
    data = await state.get_data()
    address = ", ".join([data["city"], data['region']])
    await Client.objects.filter(id=data["passport"]).aupdate(address=address)
    client = await Client.objects.aget(id=data["passport"])
    await _render_passport_with_keyboard(client, msg)
    await state.set_state(ListPassport.action)
    keyboard = await _menu_keyboard(msg)
    await msg.answer(_(MENU, msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))


async def enter_phone(msg: types.Message, state: FSMContext):
    text = _("enter_phone_text", msg.bot.lang)
    await msg.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()
    await state.set_state(ListPassport.phone)


async def entered_phone(msg: types.Message, state: FSMContext):
    from .start import _menu_keyboard
    try:
        value = await validate_phone(msg.text)
    except ValidationError as _exp:
        await msg.answer(_(_exp.message, msg.bot.lang, pnfl=msg.text))
    else:
        data = await state.get_data()
        await Client.objects.filter(id=data["passport"]).aupdate(phone=value)
        client = await Client.objects.aget(id=data["passport"])
        await _render_passport_with_keyboard(client, msg)
        await state.set_state(ListPassport.action)
        keyboard = await _menu_keyboard(msg)
        await msg.answer(_(MENU, msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))

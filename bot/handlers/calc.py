from aiogram import types, Dispatcher
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.models import get_text as _
from bot.text_keywords import CALCULATOR, MENU
from bot.filters.db_filter import DbSearchFilter
from storages.models import Storage
from bot.states import CalculatorState

def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(CALCULATOR))(storage_list)
    dp.message(CalculatorState.storage)(storage_selected)
    dp.message(CalculatorState.kg)(entered_kg)


async def storage_list(msg: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardBuilder()
    if not await Storage.objects.translated(msg.bot.lang).filter(is_active=True).aexists():
        return await msg.answer(_("storage_list_empty", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    async for storage in Storage.objects.prefetch_related("translations").translated(msg.bot.lang).filter(is_active=True):
        keyboard.row(types.KeyboardButton(text=storage.name))
    keyboard.row(types.KeyboardButton(text=_(MENU, msg.bot.lang)))
    await msg.answer(_("storage_list_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(CalculatorState.storage)


async def storage_selected(msg: types.Message, state: FSMContext):
    try:
        storage = await Storage.objects.prefetch_related("translations").aget(translations__name=msg.text, translations__language_code=msg.bot.lang)
        await _render_storage(msg, storage)
        await state.set_state(CalculatorState.kg)
        await state.update_data(storage=storage.id)
    except Storage.DoesNotExist:
        await msg.answer(_("invalid_storage", msg.bot.lang))


async def _render_storage(msg: types.Message, storage: Storage):
    text = f"""
{_('storage_name', msg.bot.lang)}: {storage.name}
{_('price_for_kg', msg.bot.lang)}: {storage.per_price} $
"""
    text = [text]
    try:
        weight = float(msg.text.replace(",", "."))
        text.append(f"{msg.text}{_('kg', msg.bot.lang)} = {storage.per_price * weight} $")
    except ValueError:
        pass
    text.append(_("enter_kg_for_calc", msg.bot.lang))
    await msg.answer("\n".join(text))


async def entered_kg(msg: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        storage = await Storage.objects.prefetch_related("translations").aget(id=data.get("storage"))
        await _render_storage(msg, storage)
    except Storage.DoesNotExist:
        await msg.answer(_("invalid_storage", msg.bot.lang))
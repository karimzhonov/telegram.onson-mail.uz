from aiogram import types, Dispatcher
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.models import get_text as _, slug_from_text
from bot.text_keywords import MENU, FAQ
from bot.filters.db_filter import DbSearchFilter
from bot.states import FAQState
from bot.models import FAQ_TYPES, FAQ as FAQModel, FAQ_TYPE_DELIVERY
from storages.models import Storage
from django.core.files.base import ContentFile


def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(FAQ))(entered_faq)
    dp.message(FAQState.type)(entered_faq_type)
    dp.message(FAQState.storage)(entered_storage_faq)
    dp.message(FAQState.text)(entered_faq_text)


async def entered_faq(msg: types.Message, state: FSMContext):
    await msg.answer(_("faq_text", msg.bot.lang))
    await enter_faq_type(msg, state)
    await state.set_state(FAQState.type)


async def enter_faq_type(msg: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardBuilder()
    for i in range(0, len(FAQ_TYPES), 2):
        keyboard.row(
            types.KeyboardButton(text=_(FAQ_TYPES[i][0], msg.bot.lang)), 
            types.KeyboardButton(text=_(FAQ_TYPES[i + 1][0], msg.bot.lang))
        )
    keyboard.row(types.KeyboardButton(text=_(MENU, msg.bot.lang)))
    await msg.answer(_("faq_type_text", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))


async def entered_faq_type(msg: types.Message, state: FSMContext):
    slug = slug_from_text(msg.text, msg.bot.lang)
    if not slug in dict(FAQ_TYPES).keys():
        return await msg.answer(_("invalid_faq_type", msg.bot.lang))
    await state.update_data(type=slug)
    if FAQ_TYPE_DELIVERY == slug:
        return await enter_faq_storage(msg, state)
    await enter_faq_text(msg, state)


async def enter_faq_storage(msg: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardBuilder()
    async for storage in Storage.objects.prefetch_related("translations").translated(msg.bot.lang).filter(is_active=True, translations__language_code=msg.bot.lang):
        keyboard.row(types.KeyboardButton(text=storage.name))
    keyboard.row(types.KeyboardButton(text=_(MENU, msg.bot.lang)))
    await msg.answer(_("storage_list_faq", msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(FAQState.storage)

async def entered_storage_faq(msg: types.Message, state: FSMContext):
    try:
        storage = await Storage.objects.prefetch_related("translations").filter(translations__name=msg.text).afirst()
        await state.update_data(storage=storage.id)
        await enter_faq_text(msg, state)
    except Storage.DoesNotExist:
        await msg.answer(_("invalid_storage", msg.bot.lang))


async def enter_faq_text(msg: types.Message, state: FSMContext):
    await msg.answer(_("faq_question_text", msg.bot.lang), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(FAQState.text)


async def entered_faq_text(msg: types.Message, state: FSMContext):
    from .start import _menu_keyboard
    data = await state.get_data()
    text = msg.text or msg.caption
    photo = await msg.bot.download(msg.photo[-1]) if msg.photo else None

    faq = await FAQModel.objects.acreate(
        text=text, type=data["type"],
        user_id=msg.from_user.id,
        message_id=msg.message_id,
        storage_id=data.get("storage")
    )
    if photo:
        await faq.save_image(ContentFile(photo.getvalue()))
    keyboard = await _menu_keyboard(msg, msg.from_user.id)
    await msg.answer(_("faq_question_text_entered", msg.bot.lang))
    await msg.answer(_(MENU, msg.bot.lang), reply_markup=keyboard.as_markup(resize_keyboard=True))

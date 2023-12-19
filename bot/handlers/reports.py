from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from bot.filters.db_filter import DbSearchFilter
from bot.filters.prefix import Prefix
from bot.models import get_text as _
from bot.text_keywords import FOTO_REPORTS
from bot.utils import get_file
from orders.models import Report

LIMIT = 5

def setup(dp: Dispatcher):
    dp.message(DbSearchFilter(FOTO_REPORTS))(my_reports)
    dp.callback_query(Prefix("report"))(report_action)


async def my_reports(msg: types.Message, state: FSMContext, offset=0, user_id=None):
    user_id = msg.from_user.id if not user_id else user_id
    reports = Report.objects.select_related("clientid", "clientid__user", "clientid__storage").filter(clientid__user_id=user_id).order_by("-create_date")
    if not await reports.aexists():
        return await msg.answer(_("report_list_empty", msg.bot.lang))
    async for report in reports[offset:offset + LIMIT]:
        photo = await sync_to_async(_render_report)(report)
        if photo:
            await msg.answer_media_group(media=photo)

    products_count = await reports.acount()
    text = f"""{_("showed_offset_reports_in_count", msg.bot.lang, offset=LIMIT + offset, count=products_count)}"""
    keyboard = InlineKeyboardBuilder()
    if LIMIT + offset < products_count:
        keyboard.row(types.InlineKeyboardButton(text=_("show_again", msg.bot.lang), callback_data=f"report:show_again:{offset + LIMIT}"))
        await msg.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


async def report_action(cq: types.CallbackQuery, state: FSMContext):
    msg = cq.message
    type, *cq_data_list = cq.data.split(":")
    if cq_data_list[0] == "show_again":
        await msg.delete()
        await my_reports(msg, state, int(cq_data_list[1]), cq.from_user.id)


def _render_report(report: Report):
    text = _render_report_text(report)
    files = []    
    for i, ri in enumerate(report.reportimage_set.all()):
        if i == 0:
            files.append(types.InputMediaPhoto(media=get_file(str(ri.image)), caption=text))
        else:
            files.append(types.InputMediaPhoto(media=get_file(str(ri.image))))    
    return files


def _render_report_text(report: Report):
    user = report.clientid.user
    return f"""
{_('foto_report', user.lang)}
{_('client_id', user.lang)}: {report.clientid}
{_('datetime', user.lang)}: {report.create_date.strftime("%d-%m-%Y %H:%M")}
        """
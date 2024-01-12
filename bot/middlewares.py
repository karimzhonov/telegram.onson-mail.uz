from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import CallbackQuery, Message
from django.conf import settings

from .models import User
from .models import get_text as _


class LanguageMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        data["lang"] = "uz"
        event.bot.lang = "uz"
        try:
            user = await User.objects.aget(id=event.from_user.id)
            data['lang'] = user.lang
            event.bot.lang = user.lang
            await user.acreate_historical_record()
        except User.DoesNotExist:
            pass
        
        if settings.DEBUG:
            message = await event.answer(_("loading", event.bot.lang))
            response = await handler(event, data)
            await message.delete()
        else:
            try:
                message = await event.answer(_("loading", event.bot.lang))
                response = await handler(event, data)
                await message.delete()
            except Exception:
                await message.answer(_("error", event.bot.lang))
        return response
    

class LanguageCallBackMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any]
    ) -> Any:
        data["lang"] = "uz"
        event.bot.lang = "uz"
        try:
            user = await User.objects.aget(id=event.from_user.id)
            data['lang'] = user.lang
            event.message.bot.lang = user.lang
        except User.DoesNotExist:
            pass
        message = await event.message.answer(_("loading", event.bot.lang))
        response = await handler(event, data)
        await message.delete()
        return response


def setup(dp: Dispatcher):
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageCallBackMiddleware())

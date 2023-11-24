from typing import Callable, Any, Awaitable
from aiogram.types import Message, CallbackQuery
from aiogram import Dispatcher, BaseMiddleware
from .models import User


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
        return await handler(event, data)
    

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
        return await handler(event, data)


def setup(dp: Dispatcher):
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageCallBackMiddleware())

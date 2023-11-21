from aiogram.types import Message
from aiogram import Bot
from aiogram.filters.base import Filter
from bot.models import Text, User


class DbSearchFilter(Filter):
    def __init__(self, slug) -> None:
        self.slug = slug

    async def __call__(self, message: Message, bot: Bot):
        if not hasattr(bot, "lang"):
            user = await User.objects.aget(id=message.from_user.id)
            bot.lang = user.lang
        return await Text.objects.filter(slug=self.slug, text=message.text, lang=bot.lang).aexists()
    
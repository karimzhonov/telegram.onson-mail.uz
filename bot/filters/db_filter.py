from aiogram import Bot
from aiogram.filters.base import Filter
from aiogram.types import Message

from bot.models import User, check_text


class DbSearchFilter(Filter):
    def __init__(self, slug) -> None:
        self.slug = slug

    async def __call__(self, message: Message, bot: Bot):
        if not hasattr(bot, "lang"):
            user = await User.objects.filter(id=message.from_user.id).afirst()
            bot.lang = user.lang if user else "uz"
            await user.acreate_historical_record()
        if not message.text:
            return False
        return check_text(self.slug, message.text, bot.lang)
    
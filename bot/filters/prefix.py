from aiogram import Bot
from aiogram.filters.base import Filter
from aiogram.types import CallbackQuery

from bot.models import User, check_text


class Prefix(Filter):
    def __init__(self, prefix) -> None:
        self.slug = prefix

    async def __call__(self, cq: CallbackQuery, bot: Bot):
        return cq.data.split(":")[0] == self.slug

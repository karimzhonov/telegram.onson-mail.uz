import os
from aiogram import Dispatcher, Bot, enums
from aiogram.fsm.storage.redis import RedisStorage
from .settings import REDIS_URL


def build_absolute_url(url):
    base_url = os.getenv("TELEGRAM_BOT_BASE_URL", "")
    return ''.join((base_url, url))


def create_dispatcher():
    return Dispatcher(
        storage=RedisStorage.from_url(REDIS_URL),
    )


def create_bot(token):
    return Bot(token, parse_mode=enums.ParseMode.HTML)

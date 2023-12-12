import os
from aiogram import Dispatcher, Bot, enums, types
from aiogram.fsm.storage.redis import RedisStorage
from PIL import Image
from django.conf import settings
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


def concat_images(images: list[Image.Image], size=(800, 800)):
    if len(images) == 1:
        images[0].thumbnail(size, Image.Resampling.LANCZOS)
        return images[0]
    new_width = max(*[image.size[0] for image in images])
    new_height = sum([image.size[1] for image in images])
    dst = Image.new('RGB', (new_width, new_height))
    height = 0
    for image in images:
        dst.paste(image, (0, height))
        height += image.size[1]
    dst.thumbnail(size, Image.Resampling.LANCZOS)
    return dst

def get_file(file_path):
    if settings.DEBUG:
        return types.BufferedInputFile.from_file(file_path)
    return f"http://178.208.81.109:8000{file_path}"
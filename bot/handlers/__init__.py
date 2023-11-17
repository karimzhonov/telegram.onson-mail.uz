from aiogram import Dispatcher
from aiogram.dispatcher.filters.builtin import CommandStart

from .start import start

def setup(dp: Dispatcher):
    dp.register_message_handler(start, CommandStart(), state="*")
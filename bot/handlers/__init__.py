from aiogram import Dispatcher
from . import storages, my_passport, register, start, about, calc


def setup(dp: Dispatcher):
    start.setup(dp)
    register.setup(dp)
    my_passport.setup(dp)
    storages.setup(dp)
    about.setup(dp)
    calc.setup(dp)

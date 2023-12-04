from aiogram import Dispatcher
from . import storages, my_passport, register, start, about, calc, online_buy, reports, faq


def setup(dp: Dispatcher):
    start.setup(dp)
    register.setup(dp)
    my_passport.setup(dp)
    online_buy.setup(dp)
    storages.setup(dp)
    about.setup(dp)
    calc.setup(dp)
    reports.setup(dp)
    faq.setup(dp)

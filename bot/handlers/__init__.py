from aiogram import Dispatcher

from . import about, calc, faq, my_passport, online_buy, register, reports, start, storages


def setup(dp: Dispatcher):
    start.setup(dp)
    register.setup(dp)
    reports.setup(dp)
    my_passport.setup(dp)
    online_buy.setup(dp)
    storages.setup(dp)
    about.setup(dp)
    calc.setup(dp)
    faq.setup(dp)

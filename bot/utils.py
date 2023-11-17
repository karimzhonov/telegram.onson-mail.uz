import os
import time
from aiogram import Dispatcher, Bot, types, executor
from aiogram.utils.exceptions import NetworkError
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from asgiref.sync import async_to_sync


def build_absolute_url(url):
    base_url = os.getenv("TELEGRAM_BOT_BASE_URL", "")
    return ''.join((base_url, url))


def setwebhook(dp: Dispatcher, webhook_url: str):
    from .settings import WEB_DOMAIN
    
    webhook = async_to_sync(dp.bot.get_webhook_info)()
    webhook_url = "".join([WEB_DOMAIN, webhook_url])
    if webhook.url != webhook_url:
        async_to_sync(dp.bot.set_webhook)(webhook_url, drop_pending_updates=True)
        print('Webhook was successfully setted!')
    else:
        print('Webhook already setted!')


def deletewebhook(dp: Dispatcher):
    webhook = async_to_sync(dp.bot.get_webhook_info)()
    if webhook.url != "":
        async_to_sync(dp.bot.delete_webhook)()
        print('Webhook was successfully deleted!')
    else:
        print('Webhook no setted!')


def create_dispatcher(token):
    return Dispatcher(
        Bot(token, parse_mode=types.ParseMode.HTML, validate_token=True),
        storage=MemoryStorage()
    )


def run_dispatcher(dp: Dispatcher):
    try:
        print("Bot started")
        executor.start_polling(dp, timeout=3, skip_updates=False, relax=1)
    except NetworkError as _exp:
        time.sleep(3)
        run_dispatcher(dp)


def run_webhook(dp: Dispatcher):
    from .settings import WEBHOOK_PATH, WEB_PORT, WEBHOOK_URL

    async def on_startup(dp: Dispatcher):
        await dp.bot.set_webhook(WEBHOOK_URL)
    
    async def on_shutdown(dp):
        print('Shutting down..')

        # insert code here to run it before shutdown

        # Remove webhook (not acceptable in some cases)
        await dp.bot.delete_webhook()

        # Close DB connection (if used)
        await dp.storage.close()
        await dp.storage.wait_closed()

        print('Bye!')

    executor.start_webhook(
        dp, WEBHOOK_PATH, skip_updates=True, host="0.0.0.0", port=WEB_PORT, on_startup=on_startup, on_shutdown=on_shutdown
    )
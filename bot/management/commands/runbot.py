import asyncio
import logging

from django.core.management import BaseCommand

from bot import handlers, middlewares
from bot.loader import dp
from bot.settings import TOKEN
from bot.utils import create_bot

logger = logging.getLogger(__name__)


async def main():
    assert TOKEN, "TELEGRAM_BOT_TOKEN not found in environment"

    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    handlers.setup(dp)
    middlewares.setup(dp)

    # start
    try:
        await dp.start_polling(create_bot(TOKEN))
    finally:
        await dp.storage.close()
        session = await dp.bot.get_session()
        await session.close()


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            logger.error("Bot stopped!")
        
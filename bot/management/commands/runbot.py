import asyncio, logging
from django.core.management import BaseCommand
from bot.loader import dp
from bot import handlers

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    handlers.setup(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await dp.bot.get_session()
        await session.close()


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            logger.error("Bot stopped!")
        
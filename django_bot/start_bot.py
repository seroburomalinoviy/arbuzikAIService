import logging
import os
from dotenv import load_dotenv
import asyncio

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.handlers.setup import init_handlers
from bot.amqp_driver import amqp_listener
from bot.logic import constants

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s >>> %(funcName)s(%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    os.makedirs(f'{constants.voices_to_process}', exist_ok=True)  # for RVC
    os.makedirs(f'{constants.voice_collection}', exist_ok=True)  # for CMS
    os.makedirs(f'{constants.image_covers}', exist_ok=True)  # for CMS

    TOKEN = os.environ.get('BOT_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()

    application = init_handlers(application)

    # async rabbit listener
    loop = asyncio.get_event_loop()
    loop.create_task(amqp_listener())

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if "__main__" == __name__:
    main()

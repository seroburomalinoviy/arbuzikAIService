import logging
import os
from dotenv import load_dotenv
import asyncio

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.logic.setup import init_handlers
from bot.logic.amqp_driver import amqp_payment_url_listener, amqp_payment_listener, amqp_rvc_listener

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    TOKEN = os.environ.get("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application = init_handlers(application)

    # async rabbit listener
    loop = asyncio.get_event_loop()
    loop.create_task(amqp_rvc_listener())
    loop.create_task(amqp_payment_url_listener())
    loop.create_task(amqp_payment_listener())

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if "__main__" == __name__:
    main()

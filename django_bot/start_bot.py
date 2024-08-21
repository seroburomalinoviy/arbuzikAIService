import os
from dotenv import load_dotenv
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.logic.setup import init_handlers
from bot.logic.amqp_driver import amqp_payment_url_listener, amqp_payment_listener, amqp_rvc_listener

load_dotenv()


def main() -> None:
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
    os.makedirs('/logs', exist_ok=True)
    handler = RotatingFileHandler('/logs/bot.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('').addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)

    main()

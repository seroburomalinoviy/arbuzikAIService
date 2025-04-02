import os
from dotenv import load_dotenv
import asyncio
import logging
from logging.config import dictConfig

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.logic.setup import init_handlers
from bot.logic.amqp.driver import amqp_listener
from bot.logic.amqp.tasks import send_payment_url, send_payment_answer, send_rvc_answer
import logging_config
import sentry_sdk
sentry_sdk.init("http://8eebad4c4a544c2abe940ced968d5cef@localhost:8000/3")

load_dotenv()


def main() -> None:
    TOKEN = os.environ.get("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application = init_handlers(application)

    # AMQP listeners
    loop = asyncio.get_event_loop()
    loop.create_task(amqp_listener("rvc-to-bot", send_rvc_answer))
    loop.create_task(amqp_listener("payment-to-bot", send_payment_answer))
    loop.create_task(amqp_listener("payment-url", send_payment_url))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if "__main__" == __name__:
    os.makedirs('/logs', exist_ok=True)
    dictConfig(logging_config.config)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    main()


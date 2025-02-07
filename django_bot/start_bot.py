import os
from dotenv import load_dotenv
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.logic.setup import init_handlers
from bot.logic.amqp_driver import amqp_listener, send_payment_url, send_payment_answer, send_rvc_answer

load_dotenv()


async def main() -> None:
    TOKEN = os.environ.get("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application = init_handlers(application)

    # AMQP listeners
    queue_func = (("rvc-to-bot", send_rvc_answer), ("payment-to-bot", send_payment_url), ("payment-url", send_payment_answer))
    tasks = [amqp_listener(queue, func) for queue, func in queue_func]
    await asyncio.gather(*tasks)

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

    asyncio.run(main())


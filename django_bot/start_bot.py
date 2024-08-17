import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv
import asyncio

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.logic.setup import init_handlers
from bot.logic.amqp_driver import amqp_payment_url_listener, amqp_payment_listener, amqp_rvc_listener



def start_rotating_logging(path):


    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    handler = RotatingFileHandler(path, backupCount=5, maxBytes=512 * 1024)
    handler.setFormatter(logging.Formatter(log_format))

    logger = logging.getLogger(__name__)
    logger.addHandler(handler)

    class CustomFilter(logging.Filter):
        COLOR = {
            "DEBUG": "GREEN",
            "INFO": "GREEN",
            "WARNING": "YELLOW",
            "ERROR": "RED",
            "CRITICAL": "RED",
        }

        def filter(self, record):
            record.color = CustomFilter.COLOR[record.levelname]
            return True

    logger.addFilter(CustomFilter())



# class CustomFilter(logging.Filter):
#     COLOR = {
#         "DEBUG": "GREEN",
#         "INFO": "GREEN",
#         "WARNING": "YELLOW",
#         "ERROR": "RED",
#         "CRITICAL": "RED",
#     }
#
#     def filter(self, record):
#         record.color = CustomFilter.COLOR[record.levelname]
#         return True
#
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - [%(levelname)s] - [%(color)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
# )
#
#
# logger = logging.getLogger(__name__)
# logger.addFilter(CustomFilter())


def main() -> None:
    load_dotenv()

    # os.makedirs('/logs', exist_ok=True)
    # rotating_handler = logging.handlers.RotatingFileHandler('/logs/bot.log', backupCount=5, maxBytes=512 * 1024)
    # log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    # formatter = logging.Formatter(log_format)
    # rotating_handler.setFormatter(formatter)
    # logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    # logging.getLogger('').addHandler(rotating_handler)

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

    start_rotating_logging(path="/logs/bot.log")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    main()

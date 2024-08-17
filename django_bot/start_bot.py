import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv
import asyncio

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.logic.setup import init_handlers
from bot.logic.amqp_driver import amqp_payment_url_listener, amqp_payment_listener, amqp_rvc_listener

load_dotenv()


# def start_rotating_logging(path):
#
#
#     log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
#     logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
#
#     handler = RotatingFileHandler(path, backupCount=5, maxBytes=512 * 1024)
#     handler.setFormatter(logging.Formatter(log_format))
#
#     logger = logging.getLogger(__name__)
#     logger.addHandler(handler)
#
#     class CustomFilter(logging.Filter):
#         COLOR = {
#             "DEBUG": "GREEN",
#             "INFO": "GREEN",
#             "WARNING": "YELLOW",
#             "ERROR": "RED",
#             "CRITICAL": "RED",
#         }
#
#         def filter(self, record):
#             record.color = CustomFilter.COLOR[record.levelname]
#             return True
#
#     logger.addFilter(CustomFilter())




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
    # os.makedirs('/logs', exist_ok=True)
    # handler = RotatingFileHandler('/logs/bot.log', backupCount=5, maxBytes=512 * 1024)
    # log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    # formatter = logging.Formatter(log_format)
    # handler.setFormatter(formatter)
    # handler.addFilter(CustomFilter())
    # logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    # logging.getLogger('').addHandler(handler)
    import logging


    class CustomFormatter(logging.Formatter):
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

        FORMATS = {
            logging.DEBUG: grey + format + reset,
            logging.INFO: grey + format + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: bold_red + format + reset
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)


    # create logger with 'spam_application'
    logger = logging.getLogger("My_app")
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    logging.getLogger("httpx").setLevel(logging.DEBUG)

    main()

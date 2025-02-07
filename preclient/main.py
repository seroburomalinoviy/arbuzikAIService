import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os

from amqp.driver import amqp_listener
from amqp.tasks import create_task


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    handler = RotatingFileHandler('/logs/preclient.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('').addHandler(handler)

    loop = asyncio.get_event_loop()
    loop.create_task(amqp_listener("bot-to-rvc", create_task))

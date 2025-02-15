import asyncio
from logging.config import dictConfig
import os

from amqp.driver import amqp_listener
from amqp.tasks import create_task
import logging_config


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    dictConfig(logging_config.config)
    # handler = RotatingFileHandler('/logs/preclient.log', backupCount=5, maxBytes=512 * 1024)
    # log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    # formatter = logging.Formatter(log_format)
    # handler.setFormatter(formatter)
    # logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    # logging.getLogger('').addHandler(handler)

    asyncio.run(amqp_listener("bot-to-rvc", create_task))

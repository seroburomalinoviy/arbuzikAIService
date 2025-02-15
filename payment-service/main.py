import asyncio
from logging.config import dictConfig
import os

from amqp.driver import amqp_listener
from amqp.aaio_request import get_payment_url
import logging_config


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    # handler = RotatingFileHandler('/logs/payment-listener.log', backupCount=5, maxBytes=512 * 1024)
    # log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    # formatter = logging.Formatter(log_format)
    # handler.setFormatter(formatter)
    # logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    # logging.getLogger('').addHandler(handler)
    dictConfig(logging_config.config)

    asyncio.run(amqp_listener("payment-url", get_payment_url))


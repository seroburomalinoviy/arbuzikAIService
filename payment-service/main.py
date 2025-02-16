import asyncio
from logging.config import dictConfig
import os

from amqp.driver import amqp_listener
from amqp.aaio_request import get_payment_url
import logging_config


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    dictConfig(logging_config.config)

    asyncio.run(amqp_listener("payment-url", get_payment_url))


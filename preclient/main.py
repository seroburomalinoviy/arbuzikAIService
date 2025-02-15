import asyncio
from logging.config import dictConfig
import os

from amqp.driver import amqp_listener
from amqp.tasks import create_task
import logging_config


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    dictConfig(logging_config.config)

    asyncio.run(amqp_listener("bot-to-rvc", create_task))

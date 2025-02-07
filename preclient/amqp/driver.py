import aio_pika
import os
import logging
from typing import Callable, Awaitable
import asyncio

AsyncFunc = Callable[[str], Awaitable[None]]


class PikaConnector:
    @classmethod
    async def connector(cls):
        try:
            connector = await aio_pika.connect_robust(
                host=os.getenv("RABBIT_HOST"),
                port=int(os.getenv("RABBIT_PORT")),
                login=os.getenv("RABBIT_USER"),
                password=os.getenv("RABBIT_PASSWORD"),
            )
            logging.info(f"Preclient connected to rabbit")
            return connector
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
            logging.error(e)
            await asyncio.sleep(3)
            return await cls.connector()


def _amqp_message_handler(func: AsyncFunc):
    async def process_message(message: aio_pika.IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            logging.info(f"Preclient got msg from rabbit:\n{msg}")
            await func(msg)
    return process_message


async def amqp_listener(queue_name: str, func: AsyncFunc):
    connection = await PikaConnector.connector()
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name)

    await queue.consume(_amqp_message_handler(func))
    return connection


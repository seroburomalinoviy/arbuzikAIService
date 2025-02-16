import logging
import os
import aio_pika
import json
import asyncio
from typing import Awaitable, Callable
import traceback

logger = logging.getLogger(__name__)

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
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
            logger.error(e)
            await asyncio.sleep(3)
            return await cls.connector()
        except:
            logger.error(f"Uncaught error: {traceback.format_exc()}")
            await asyncio.sleep(3)
            return await cls.connector()
        else:
            logger.info(f"Connected from Bot to RabbitMQ")
            return connector


async def push_amqp_message(data: dict, routing_key: str) -> None:
    payload = json.dumps(data)
    connection = await PikaConnector.connector()

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(routing_key, durable=True)
        await channel.default_exchange.publish(
            # delivery_mode ...PERSISTENT: сообщения будут сохраняться на диске,
            # что позволяет предотвратить их потерю при сбоях RabbitMQ
            aio_pika.Message(body=payload.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=queue.name,
        )
    logger.info(f"A message from Bot to RVC (by Preclient over RabbitMQ)\n{payload} ")


def _amqp_message_handler(task: AsyncFunc):
    async def process_message(message: aio_pika.IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            logger.info(f"A message from RVC to Bot\n{msg}")
            await task(msg)
    return process_message


async def amqp_listener(queue_name: str, task: AsyncFunc):
    connection = await PikaConnector.connector()
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, durable=True)

    await queue.consume(_amqp_message_handler(task))
    await asyncio.Future()

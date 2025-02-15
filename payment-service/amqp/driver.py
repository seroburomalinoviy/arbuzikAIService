import aio_pika
import os
import logging
from typing import Callable, Awaitable
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()

AsyncFunc = Callable[[str], Awaitable[None]]


class PikaConnector:
    @classmethod
    async def connector(cls):
        try:
            connector = await aio_pika.connect_robust(
                host=os.environ.get("RABBIT_HOST"),
                port=int(os.environ.get("RABBIT_PORT")),
                login=os.environ.get("RABBIT_USER"),
                password=os.environ.get("RABBIT_PASSWORD"),
            )
            logging.info(f"Connected from Payment to RabbitMQ")
            return connector
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
            logging.error(e)
            await asyncio.sleep(3)
            return await cls.connector()


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
    logging.info(f"A message from Payment to Bot (over RabbitMQ)\n{payload} ")


def _amqp_message_handler(func: AsyncFunc):
    async def process_message(message: aio_pika.IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            logging.info(f"A message from Bot to Payment (by RabbitMQ):\n{msg}")
            await func(msg)
    return process_message


async def amqp_listener(queue_name: str, func: AsyncFunc):
    connection = await PikaConnector.connector()
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, durable=True)

    await queue.consume(_amqp_message_handler(func))
    await asyncio.Future()



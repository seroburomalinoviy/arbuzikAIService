import logging
import os
from dotenv import load_dotenv
import aio_pika
import json
import asyncio

from aaio_request import get_payment_url

load_dotenv()

logger = logging.getLogger(__name__)


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
            logger.info(f"Connected to rabbit")
            return connector
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
            logger.error(e)
            await asyncio.sleep(3)
            return await cls.connector()


async def amqp_listener():

    connection = await PikaConnector.connector()

    queue_name = "bot-to-payment"

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=True)

        logger.debug(f"get queue {queue_name} from rabbit")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():

                    data: dict = await get_payment_url(message.body)
                    await push_amqp_message(data, routing_key='payment-url')

                    if queue.name in message.body.decode():
                        break


async def push_amqp_message(data: dict, routing_key):
    payload = json.dumps(data)
    connection = await PikaConnector.connector()

    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=payload.encode()),
            routing_key=routing_key,
        )
    logger.info(f"message {payload} sent to rabbit {routing_key=}")




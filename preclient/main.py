import asyncio
from redis import asyncio as aioredis
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv
import aio_pika

load_dotenv()


async def create_task(payload):
    # https://aioredis.readthedocs.io/en/latest/getting-started/
    logging.info(f"redis input args: {payload}")

    redis = aioredis.from_url(
        url=f"redis://{os.environ.get('REDIS_HOST')}"
    )
    pubsub = redis.pubsub()
    await pubsub.subscribe("channel:raw-data")
    await redis.publish("channel:raw-data", payload)

    logging.info("message send to redis")


async def task_listener():
    logging.debug("Start task listener")
    connection = await aio_pika.connect_robust(
        host=os.environ.get("RABBIT_HOST"),
        port=int(os.environ.get("RABBIT_PORT")),
        login=os.environ.get("RABBIT_USER"),
        password=os.environ.get("RABBIT_PASSWORD"),
    )
    logging.debug("Connection with rabbitmq established")

    queue_name = "bot-to-rvc"

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():

                    logging.info(f"preclient get message {queue_name=}: {message.body.decode()}")

                    await create_task(message.body.decode())

                    if queue.name in message.body.decode():
                        break


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    rotating_handler = RotatingFileHandler('/logs/preclient.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    rotating_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('').addHandler(rotating_handler)
    
    asyncio.run(task_listener())

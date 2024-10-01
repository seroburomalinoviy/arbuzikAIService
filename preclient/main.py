import asyncio
import json

import redis
from redis.exceptions import ConnectionError, DataError, NoScriptError, RedisError, ResponseError
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv
import aio_pika

load_dotenv()


async def create_task(payload: str):
    payload: dict = json.loads(payload)
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        port=os.environ.get('REDIS_PORT'),
        retry_on_timeout=True
    )
    stream_key = "raw-data"
    payload['count_tasks'] = r.xlen("raw-data")
    resp = r.xadd(stream_key, payload)

    logging.info(resp)
    logging.info(f"The {stream_key} stream's length: {r.xlen(stream_key)}")


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
    handler = RotatingFileHandler('/logs/preclient.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('').addHandler(handler)
    
    asyncio.run(task_listener())

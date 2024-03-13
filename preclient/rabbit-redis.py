import asyncio
from redis import asyncio as aioredis
import logging
import os
from dotenv import load_dotenv
import aio_pika
import sentry_sdk

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s >>> %(funcName)s(%(lineno)d)",
    datefmt="%Y-%m-%d %H:%M:%S",
)

sentry_sdk.init(
    dsn="https://674f9f3c6530ddb20607dd9a42413fa4@o4506896610885632.ingest.us.sentry.io/4506896620978176",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

load_dotenv()


async def create_task(user_id, filename, pitch):
    # https://aioredis.readthedocs.io/en/latest/getting-started/
    logger.info(f'redis input args: {user_id=}, {filename=}, {pitch=}')
    redis = aioredis.from_url(
        url=f"redis://2.56.91.74"  # todo: можем ли использовать сеть докеров? Оптимально?
    )
    await redis.hset(f"key-{user_id}", mapping={"pitch": f"{pitch}", "voice-raw": f"{filename}"})
    logger.debug('message added to redis')


async def task_listener():
    logger.debug('Start task listener')
    connection = await aio_pika.connect_robust(
        host=os.environ.get('RABBIT_HOST'),
        port=int(os.environ.get('RABBIT_PORT')),
        login=os.environ.get('RABBIT_USER'),
        password=os.environ.get('RABBIT_PASSWORD'),
    )
    logger.debug('Connection with rabbitmq established')
    queue_name = "bot-to-rvc"

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=True)
        logger.debug('get queue from rabbit')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():

                    await create_task(*message.body.decode().split("_"))

                    if queue.name in message.body.decode():
                        break


if __name__ == '__main__':
    asyncio.run(task_listener())

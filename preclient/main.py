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


async def create_task(payload):
    # https://aioredis.readthedocs.io/en/latest/getting-started/
    logger.info(f'redis input args: {payload}')
    redis = aioredis.from_url(
        url=f"redis://{os.environ.get('REDIS_HOST')}"  # TODO: можем ли использовать сеть докеров? Оптимально?
    )
    pubsub = redis.pubsub()
    await pubsub.subscribe("channel:raw-data")
    await redis.publish("channel:raw-data", payload)
    logger.debug('message send to redis')


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
        logger.debug(f'get queue {queue_name} from rabbit')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logger.info(f'message.body.decode() = {message.body.decode()}')
                    await create_task(message.body.decode())

                    if queue.name in message.body.decode():
                        break


if __name__ == '__main__':
    # Почему не создавать один коннекшн и использовать его
    # Сейчас для каждой записи создается конекшн и даже не закрывается
    asyncio.run(task_listener())

import asyncio
from redis import asyncio as aioredis
import logging
import os
from dotenv import load_dotenv
import aio_pika

load_dotenv()

logger = logging.getLogger(__name__)


async def create_task(user_id, pitch, filename):
    # todo: определить какие данные получаем
    # todo: использовать хеш таблицы redis'a
    # дока https://aioredis.readthedocs.io/en/latest/getting-started/
    redis = aioredis.from_url(
        url=f"redis://localhost"
    )
    await redis.hset(f"{user_id}", mapping={"pitch": f"{pitch}", "filename": f"{filename}"})
    logger.info('message added to redis')


async def task_listener():
    logger.info('Start task listener')
    connection = await aio_pika.connect_robust(
        host=os.environ.get('RABBIT_HOST'),
        port=int(os.environ.get('RABBIT_PORT')),
        login=os.environ.get('RABBIT_USER'),
        password=os.environ.get('RABBIT_PASSWORD'),
    )
    logger.info('add connection')
    queue_name = "bot-to-rvc"

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logger.info(f'Message I got: {message.body}')

                    await create_task(*message.body)

                    if queue.name in message.body.decode():
                        break


if '__name__' == '__main__':
    logger.info('Start preclient!')
    asyncio.run(task_listener())

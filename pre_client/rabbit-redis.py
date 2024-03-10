import asyncio
import aioredis
import logging
import os
from dotenv import load_dotenv
import aio_pika

load_dotenv()

logger = logging.getLogger(__name__)


async def create_task(user_id, pitch, filename):
    redis = aioredis.from_url("redis://localhost")
    await redis.set("my-key", "value")


async def task_listener():

    connection = await aio_pika.connect_robust(
        host=os.environ.get('RABBIT_HOST'),
        port=int(os.environ.get('RABBIT_PORT')),
        login=os.environ.get('RABBIT_USER'),
        password=os.environ.get('RABBIT_PASSWORD'),
    )

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
    asyncio.run(task_listener())

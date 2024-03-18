import logging
import os
import asyncio

import async_timeout
from redis import asyncio as aioredis
from dotenv import load_dotenv



load_dotenv()
logger = logging.getLogger(__name__)


async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:

                    # call Mangio-RVC
                    user_id, pitch, filename = message.get("data").decode().split('_')
                    logger.info(f'Message delivered: {user_id=}, {pitch=}, {filename}')

                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass


async def main():
    try:
        redis = aioredis.from_url(
            url=f"redis://{os.environ.get('REDIS_HOST')}",
        )
    except Exception as e:
        logger.info(f'[{type(e).__name__}] - {e}')

    pubsub = redis.pubsub()
    await pubsub.subscribe("channel:raw-data")
    await asyncio.create_task(reader(pubsub))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s >>> %(funcName)s(%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    try:
        asyncio.run(main())
    except Exception as e:
        logger.info(f'[{type(e).__name__}] - {e}')



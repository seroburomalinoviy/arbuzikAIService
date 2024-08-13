import asyncio
import logging
import os
from dotenv import load_dotenv
import aio_pika

from aaio_api import make_payment

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def broker_listener():
    logger.debug("Begin listening")

    connection = await aio_pika.connect_robust(
        host=os.environ.get("RABBIT_HOST"),
        port=int(os.environ.get("RABBIT_PORT")),
        login=os.environ.get("RABBIT_USER"),
        password=os.environ.get("RABBIT_PASSWORD"),
    )
    logger.debug("Connection with rabbitmq established")

    queue_name = "payment"

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=True)

        logger.debug(f"get queue {queue_name} from rabbit")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await make_payment(message.body.decode())

                    if queue.name in message.body.decode():
                        break


if __name__ == "__main__":
    asyncio.run(broker_listener())

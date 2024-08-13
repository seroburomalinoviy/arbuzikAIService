import asyncio
from ampq_driver import amqp_listener


if __name__ == "__main__":
    asyncio.run(amqp_listener())


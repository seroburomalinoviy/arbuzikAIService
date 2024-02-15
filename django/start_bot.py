import logging
import os
from dotenv import load_dotenv
import asyncio
import pika
import aioamqp

from telegram.ext import ApplicationBuilder
from telegram import Update

from bot.handlers.setup import init_handlers

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


# async def rabbit_consumer():
#     transport, protocol = await aioamqp.connect(os.environ.get('RABBIT_HOST'), login_method="PLAIN")
#     channel = await protocol.channel()
#
#     await channel.queue_declare(queue_name='hello', arguments={'x-message-ttl': 3600000})
#
#     await channel.basic_consume(callback, queue_name='client_bot', no_ack=True)
#
#     credentials = pika.PlainCredentials(
#         os.environ.get('RABBIT_USER'),
#         os.environ.get('RABBIT_PASSWORD'))
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(
#             os.environ.get('RABBIT_HOST'),
#             int(os.environ.get('RABBIT_PORT')
#                 ),
#             '/', credentials, heartbeat=0, socket_timeout=7)
#     )
#     channel = connection.channel()
#     channel.queue_declare(queue='hello')
#
#     def callback(ch, method, properties, body):
#         print(f" [x] Received {body}")
#
#     channel.basic_consume(queue='hello', on_message_callback = callback, auto_ack = True)
#     print(' [*] Waiting for messages. To exit press CTRL+C')
#     channel.start_consuming()


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s >>> %(funcName)s(%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    TOKEN = os.environ.get('BOT_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()

    application = init_handlers(application)

    # loop = asyncio.get_event_loop()
    # loop.create_task(rabbit_consumer())

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if "__main__" == __name__:
    main()

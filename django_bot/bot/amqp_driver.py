import logging
import os
from dotenv import load_dotenv
import aio_pika
import json
from telegram import Bot

load_dotenv()

logger = logging.getLogger(__name__)
import sentry_sdk

sentry_sdk.init(
    dsn="https://674f9f3c6530ddb20607dd9a42413fa4@o4506896610885632.ingest.us.sentry.io/4506896620978176",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


async def send_answer(message):
    bot = Bot(token=os.environ.get('BOT_TOKEN'))
    payload = json.loads(message)
    chat_id = payload.get('chat_id')
    voice_id = payload.get('voice_id')
    voice_path =  os.environ.get('RABBIT_HOST') + os.environ.get('USER_VOICES_PROCESSED_VOLUME') + '/' + voice_id
    # $url = 'https://api.telegram.org/bot'.token.'/sendVideo?chat_id='.uid."&video=".$file."&caption="

    logger.info(f'voice_path: {voice_path}')
    # await bot.send_message(chat_id=chat_id, text='Получай сука')

    await bot.send_voice(chat_id=chat_id, voice=open(voice_path, 'rb'))


async def push_amqp_message(payload):
    connection = await aio_pika.connect_robust(
        host=os.environ.get('RABBIT_HOST'),
        port=int(os.environ.get('RABBIT_PORT')),
        login=os.environ.get('RABBIT_USER'),
        password=os.environ.get('RABBIT_PASSWORD'),
    )
    logger.info('Connected to rabbit')
    queue_name = "bot-to-rvc"
    routing_key = "bot-to-rvc"
    exchange_name = ''

    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=payload.encode()),
            routing_key=routing_key,
        )
    logger.info(f'message {payload} sent to rabbit')


async def amqp_listener():
    connection = await aio_pika.connect_robust(
        host=os.environ.get('RABBIT_HOST'),
        port=int(os.environ.get('RABBIT_PORT')),
        login=os.environ.get('RABBIT_USER'),
        password=os.environ.get('RABBIT_PASSWORD'),
    )
    logger.info(f'Connected to rabbit')

    queue_name = "rvc-to-bot"

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declaring queue
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logger.info(f'bot got msg from rabbit: {message.body}')

                    await send_answer(message.body)

                    if queue.name in message.body.decode():
                        break


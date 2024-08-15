import logging
import os
from dotenv import load_dotenv
import aio_pika
import json
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
import asyncio
import django
from datetime import timedelta

from bot.logic import message_text, keyboards
from bot.logic.constants import *
from bot.logic.utils import get_moscow_time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from user.models import Order

load_dotenv()

logger = logging.getLogger(__name__)


class PikaConnector:
    @classmethod
    async def connector(cls):
        try:
            connector = await aio_pika.connect_robust(
                host=os.environ.get("RABBIT_HOST"),
                port=int(os.environ.get("RABBIT_PORT")),
                login=os.environ.get("RABBIT_USER"),
                password=os.environ.get("RABBIT_PASSWORD"),
            )
            logger.info(f"Connected to rabbit")
            return connector
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
            logger.error(e)
            await asyncio.sleep(3)
            return await cls.connector()


class AnswerSerializer:
    """Serialize json answer to an object with attributes and extra attribute bot"""
    def __init__(self, _json):
        self.bot = Bot(token=os.environ.get("BOT_TOKEN"))
        data = json.loads(_json)
        for key, value in data.items():
            setattr(self, key, value)


async def send_payment_answer(data):
    payment = AnswerSerializer(data)
    order = await Order.objects.select_related("user", "subscription").aget(id=payment.order_id)
    order.status = 'paid' if payment.success else 'failure'
    order.currency = payment.currency
    order.amount = payment.amount

    if not payment.success:
        await order.asave()
        await payment.bot.send_message(
            chat_id=payment.chat_id,
            text='Оплата не прошла'
        )
    else:
        order.user.subscription = order.subscription
        order.user.subscription_status = True
        order.user.subscription_final_date = get_moscow_time() + timedelta(days=order.subscription.days_limit)
        await order.asave()
        await payment.bot.send_message(
            chat_id=payment.chat_id,
            text='Оплата прошла успешно'
        )


async def send_payment_url(data):
    payment_page = AnswerSerializer(data)

    logger.info(f'Sent payment url to {payment_page.chat_id}')

    await payment_page.bot.send_message(
        chat_id=payment_page.chat_id,
        text=message_text.payment_url,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Оплатить подписку", url=payment_page.url)]
            ]
        )
    )


async def send_rvc_answer(data):
    """
    Send voice to user from RVC-NN
    """
    audio = AnswerSerializer(data)

    file_path = os.environ.get("USER_VOICES") + "/" + audio.voice_filename

    logger.debug(f"file_path: {file_path}")

    if audio.extension == ".ogg":
        await audio.bot.send_voice(chat_id=audio.chat_id, voice=open(file_path, "rb"))
    else:
        await audio.bot.send_audio(
            chat_id=audio.chat_id,
            audio=open(file_path, "rb"),
            title=audio.voice_title,
            duration=audio.duration,
            filename=audio.voice_title,
        )

    await audio.bot.send_message(
        chat_id=audio.chat_id,
        text=message_text.final_message.format(title=audio.voice_title),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboards.final_buttons),
    )

    # todo: не удалять а перемещать в директорию /tmp
    os.remove(file_path)
    os.remove(file_path + ".tmp")

    logger.info("Voice files removed")


async def push_amqp_message(data: dict, routing_key):
    payload = json.dumps(data)
    connection = await PikaConnector.connector()

    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=payload.encode()),
            routing_key=routing_key,
        )
    logger.info(f"message {payload} sent to rabbit")


async def amqp_rvc_listener():
    connection = await PikaConnector.connector()

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declaring queue rvc-to-bot
        queue = await channel.declare_queue(name="rvc-to-bot", durable=True, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logger.info(f"bot got msg from rabbit: {message.body}")

                    await send_rvc_answer(message.body)
                    logger.info(f'{message.body.decode()=}')

                    if queue.name in message.body.decode():
                        break


async def amqp_payment_listener():
    connection = await PikaConnector.connector()

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declaring queue payment-to-bot
        queue = await channel.declare_queue(name="payment-to-bot", durable=True, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logger.info(f"bot got msg from rabbit: {message.body}")

                    await send_payment_answer(message.body)
                    logger.info(f'{message.body.decode()=}')

                    if queue.name in message.body.decode():
                        break


async def amqp_payment_url_listener():
    connection = await PikaConnector.connector()

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declaring queue payment-url
        queue = await channel.declare_queue(name="payment-url", durable=True, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logger.info(f"bot got msg from rabbit: {message.body}")

                    await send_payment_url(message.body)

                    if queue.name in message.body.decode():
                        break

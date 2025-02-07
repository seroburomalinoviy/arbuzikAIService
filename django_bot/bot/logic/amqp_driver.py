import logging
import os
from dotenv import load_dotenv
import aio_pika
import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
import asyncio
import aiofiles
import django
from datetime import timedelta

from bot.logic import message_text, keyboards
from bot.logic.constants import *
from bot.logic.utils import get_moscow_time
from bot.structures.schemas import PayUrl, RVCData, Payment
from bot.tasks import check_pay_ukassa

from typing import Awaitable, Callable


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from user.models import Order

load_dotenv()

AsyncFunc = Callable[[str], Awaitable[None]]


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
            logging.info(f"Connected to rabbit")
            return connector
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
            logging.error(e)
            await asyncio.sleep(3)
            return await cls.connector()


async def send_payment_answer(data: str):
    payment = Payment(**json.loads(data))
    order = await Order.objects.select_related("user", "subscription").aget(id=payment.order_id)

    # if payment.service == "aaio":
    order.status = payment.status
    order.currency = payment.currency
    order.amount = payment.amount
    await order.asave()
    chat_id = order.user.telegram_id

    if not payment.status:
        await payment.bot.send_message(
            chat_id=chat_id,
            text='Оплата не прошла'
        )
    else:
        # await order.asave()  # TODO проверить
        order.user.subscription = order.subscription
        order.user.subscription_status = True
        order.user.subscription_final_date = get_moscow_time() + timedelta(days=order.subscription.days_limit)
        await order.user.asave()
        await payment.bot.send_message(
            chat_id=chat_id,
            text=message_text.successful_payment.format(
                sub_title=order.subscription.telegram_title[1:],
                days=order.subscription.days_limit,
                minutes=str(int(order.user.subscription.time_voice_limit / 60)),
                vip='+' if order.user.subscription.title == 'violetvip' else 'кроме'
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboards.category_menu_2),
            disable_web_page_preview=True
        )


async def send_payment_url(data: str):
    logging.info(f'send_payment_url: {data=}')
    payment_page = PayUrl(**json.loads(data))

    last_timer = int(os.environ.get('UKASSA_TIME_WAITING_PAYMENT_MIN', 11))
    for timer in range(1, last_timer+1, 4):
        check_pay_ukassa.apply_async(args=[payment_page.order_id, payment_page.payment_id, timer], countdown=60*timer)

    logging.info(f'Sending payment url to {payment_page.chat_id}')

    await payment_page.bot.send_message(
        chat_id=payment_page.chat_id,
        text=message_text.payment_url,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Оплатить", url=payment_page.url)]
            ]
        )
    )


async def send_rvc_answer(data: str):
    """
    Send voice to user from RVC-NN
    """
    audio = RVCData(**json.loads(data))

    file_path = os.environ.get("USER_VOICES") + "/" + audio.voice_filename
    async with aiofiles.open(file_path, 'rb') as f:
        voice_file_data = await f.read()

    logging.debug(f"file_path: {file_path}")

    await audio.bot.delete_message(
        chat_id=audio.chat_id,
        message_id=audio.message_id
    )

    if audio.extension == ".ogg":
        await audio.bot.send_voice(chat_id=audio.chat_id, voice=voice_file_data)
    else:
        await audio.bot.send_audio(
            chat_id=audio.chat_id,
            audio=voice_file_data,
            duration=audio.duration,
            filename=audio.voice_title,
        )

    await audio.bot.send_message(
        chat_id=audio.chat_id,
        text=message_text.final_message.format(title=audio.voice_title),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboards.final_buttons),
    )


async def push_amqp_message(data: dict, routing_key):
    payload = json.dumps(data)
    connection = await PikaConnector.connector()

    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=payload.encode()),
            routing_key=routing_key,
        )
    logging.info(f"message {payload} sent to rabbit")


def amqp_message_handler(func: AsyncFunc):
    async def process_message(message: aio_pika.IncomingMessage):
        async with message.process():
            msg = message.body.decode()
            logging.info(f"{func.__name__} got msg from rabbit: {msg}")
            await func(msg)
    return process_message


async def amqp_listener(queue_name: str, func: AsyncFunc):
    connection = await PikaConnector.connector()
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, durable=True)

    await queue.consume(amqp_message_handler(func))
    return connection



    # async with connection:  # ????
    #     # Creating channel
    #     channel = await connection.channel()
    #
    #     # Will take no more than 10 messages in advance
    #     await channel.set_qos(prefetch_count=1000)  #
    #
    #     # Declaring queue rvc-to-bot
    #     queue = await channel.declare_queue(name="rvc-to-bot", durable=True, auto_delete=True)  # ??? auto_delete???
    #
    #     async with queue.iterator() as queue_iter:
    #         async for message in queue_iter:
    #             async with message.process():
    #                 logging.info(f"bot got msg from rabbit: {message.body.decode()}")
    #
    #                 await send_rvc_answer(message.body.decode())
    #
    #                 if queue.name in message.body.decode():
    #                     break


# async def amqp_payment_listener():
#     connection = await PikaConnector.connector()
#
#     async with connection:
#         # Creating channel
#         channel = await connection.channel()
#
#         # Will take no more than 10 messages in advance
#         await channel.set_qos(prefetch_count=1000)
#
#         # Declaring queue payment-to-bot
#         queue = await channel.declare_queue(name="payment-to-bot", durable=True, auto_delete=True)
#
#         async with queue.iterator() as queue_iter:
#             async for message in queue_iter:
#                 async with message.process():
#                     logging.info(f"bot got msg from rabbit: {message.body.decode()}")
#
#                     await send_payment_answer(message.body.decode())
#
#                     if queue.name in message.body.decode():
#                         break


# async def amqp_payment_url_listener():
#     connection = await PikaConnector.connector()
#
#     async with connection:
#         # Creating channel
#         channel = await connection.channel()
#
#         # Will take no more than 10 messages in advance
#         await channel.set_qos(prefetch_count=10000)
#
#         # Declaring queue payment-url
#         queue = await channel.declare_queue(name="payment-url", durable=True, auto_delete=True)
#
#         async with queue.iterator() as queue_iter:
#             async for message in queue_iter:
#                 async with message.process():
#                     logging.info(f"bot got msg from rabbit: {message.body.decode()}")
#
#                     await send_payment_url(message.body.decode())
#
#                     if queue.name in message.body.decode():
#                         break

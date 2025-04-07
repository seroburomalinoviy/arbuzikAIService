import logging
import os
import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
import aiofiles
import django
from datetime import timedelta

from bot.logic import message_text, keyboards
from bot.logic.utils import get_moscow_time, connection
from bot.structures.schemas import PayUrl, RVCData, Payment
from bot.tasks import check_pay_ukassa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from user.models import Order

logger = logging.getLogger(__name__)


@connection
async def send_payment_answer(data: str):
    """
    Send answer from Payment to Bot after got payment
    :param data:
    :return:
    """
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


@connection
async def send_payment_url(data: str):
    """
    Send the generated url for payment to Bot
    :param data:
    :return:
    """
    logger.info(f'send_payment_url:\n{data=}')
    payment_page = PayUrl(**json.loads(data))

    last_timer = int(os.getenv('UKASSA_TIME_WAITING_PAYMENT_MIN', 11))
    for timer in range(1, last_timer+1, 4):
        check_pay_ukassa.apply_async(args=[payment_page.order_id, payment_page.payment_id, timer], countdown=60*timer)

    logger.info(f'Sending payment url to {payment_page.chat_id}')

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


@connection
async def send_rvc_answer(data: str):
    """
    Send the answer from RVC to Bot
    :param data:
    :return:
    """
    audio = RVCData(**json.loads(data))

    file_path = os.getenv("USER_VOICES") + "/" + audio.voice_filename
    async with aiofiles.open(file_path, 'rb') as f:
        voice_file_data = await f.read()

    logger.info(f"file_path: {file_path}")

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
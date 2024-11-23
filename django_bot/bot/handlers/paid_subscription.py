from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import os
import logging

from bot.logic.utils import log_journal
from bot.logic import message_text
from bot.logic.constants import *
from bot.logic.amqp_driver import push_amqp_message
from bot.tasks import check_payment_api

from django.conf import settings
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from bot.models import Subscription
from user.models import User, Order


@log_journal
async def show_paid_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE, offer=None):
    """
    Если есть апдейт значит функция вызвана ботом, чтобы сообщить, что его подписка закончилась
    Иначе функция вызвана юзером нажатием кнопки
    :param update:
    :param offer:
    :param context:
    :return:
    """
    await update.callback_query.answer()

    if offer:
        button_text = "⏩ Вернуться в меню"
        message = message_text.offer_subscription_text
    else:
        message = message_text.all_paid_subs
        button_text = "⏩ Перейти к выбору голосов"

    keyboard = list()
    async for sub in Subscription.objects.exclude(
        title=os.environ.get("DEFAULT_SUBSCRIPTION")
    ).all().order_by("price"):
        sub_title = sub.title
        keyboard.append(
            [
                InlineKeyboardButton(
                    sub.telegram_title, callback_data=f"paid_subscription_{sub_title}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                button_text, callback_data="category_menu"
            )
        ]
    )

    demo_sub = await Subscription.objects.aget(
        title=os.environ.get("DEFAULT_SUBSCRIPTION")
    )

    await context.bot.send_photo(
        chat_id=update.effective_chat.id if update.message else update.callback_query.from_user.id,
        photo=open(
            str(settings.MEDIA_ROOT) + "/" + str(demo_sub.image_cover), "rb"
        ),  # в демо подписке лежит специальная картинка
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id if update.message else update.callback_query.from_user.id,
        text=message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return BASE_STATES


@log_journal
async def preview_paid_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE, subscription_title=None, offer=None):
    """
    Если в сообщении есть апдейт значит функция вызвана ботом при попытке пользователя записать вип
    голос без вип подписки
    Иначе эта функция вызвана юзером нажатием кнопки
    :param update:
    :param offer:
    :param context:
    :param subscription_title:
    :return:
    """
    await update.callback_query.answer()

    if offer:
        title = subscription_title
        message = message_text.offer_vip_subscription_text
    else:
        title = update.callback_query.data.split("paid_subscription_")[1]
        message = None

    subscription = await Subscription.objects.aget(title=title)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id if update.message else update.callback_query.from_user.id,
        photo=open(
            str(settings.MEDIA_ROOT) + "/" + str(subscription.image_cover), "rb"
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id if update.message else update.callback_query.from_user.id,
        text=message if message else subscription.description,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f" 💵 Разовый платёж - {subscription.price} руб",
                        callback_data=f"payment_{subscription.price}_{title}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "▶️ Другие подписки", callback_data="paid_subscriptions"
                    )
                ],
            ]
        ),
    )

    return BASE_STATES


@log_journal
async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id

    amount = query.data.split("_")[1]
    sub_title = query.data.split("_")[2]

    user = await User.objects.aget(telegram_id=chat_id)
    subscription = await Subscription.objects.aget(title=sub_title)

    order = await Order.objects.acreate(
        status=False,
        user=user,
        subscription=subscription,
        comment=f'Заказ создан, ожидается оплата'
    )

    data = {
        'subscription_title': subscription.telegram_title,
        'order_id': str(order.id),
        'amount': amount,
        'chat_id': chat_id
    }

    await push_amqp_message(data, routing_key='bot-to-payment')

    # проверка оплаты через 20 минут
    time_waiting = 60 * int(os.environ.get('TIME_WAITING_PAYMENT_MIN'), 30)
    check_payment_api.apply_async(args=[str(order.id)], countdown=time_waiting)

    return BASE_STATES



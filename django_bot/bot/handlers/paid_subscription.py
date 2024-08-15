from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import os
import logging
logger = logging.getLogger(__name__)

from django.conf import settings
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from bot.models import Subscription
from user.models import User, Order
from bot.logic.utils import log_journal
from bot.logic import message_text
from bot.logic.constants import *
from bot.logic.amqp_driver import push_amqp_message


# @log_journal
# async def offer_vip_subscription(update, context):
#     chat_id = (
#         update.effective_chat.id
#         if update.message
#         else update.callback_query.message.chat.id
#     )
#     subscription_title = "violetvip"
#     subscription = await Subscription.objects.aget(title=subscription_title)
#
#     await context.bot.send_photo(
#         chat_id=chat_id,
#         photo=open(
#             str(settings.MEDIA_ROOT) + "/" + str(subscription.image_cover), "rb"
#         ),
#     )
#
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text=message_text.offer_vip_subscription_text,
#         parse_mode=ParseMode.MARKDOWN,
#         reply_markup=InlineKeyboardMarkup(
#             [
#                 [
#                     InlineKeyboardButton(
#                         f" 💵 Разовый платёж - {subscription.price} руб",
#                         callback_data=f"payment_{subscription.price}_{subscription.title}",
#                     )
#                 ],
#                 [
#                     InlineKeyboardButton(
#                         "▶️ Другие подписки", callback_data="paid_subscriptions"
#                     ),
#                     InlineKeyboardButton(
#                         "⏩ Вернуться в меню", callback_data="category_menu"
#                     ),
#                 ],
#             ]
#         ),
#     )


# @log_journal
# async def offer_subscriptions(update: Update, context):
#     chat_id = (
#         update.effective_chat.id
#         if update.message
#         else update.callback_query.message.chat.id
#     )
#     keyboard = list()
#     async for sub in Subscription.objects.exclude(title=os.environ.get("DEFAULT_SUBSCRIPTION")).all().order_by("price"):
#         sub_title = sub.title
#         keyboard.append(
#             [
#                 InlineKeyboardButton(
#                     sub.telegram_title, callback_data=f"paid_subscription_{sub_title}"
#                 )
#             ]
#         )
#
#     keyboard.append(
#         [InlineKeyboardButton("⏩ Вернуться в меню", callback_data="category_menu")]
#     )
#
#     demo_sub = await Subscription.objects.aget(
#         title=os.environ.get("DEFAULT_SUBSCRIPTION")
#     )
#
#     await context.bot.send_photo(
#         chat_id=chat_id,
#         photo=open(
#             str(settings.MEDIA_ROOT) + "/" + str(demo_sub.image_cover), "rb"
#         ),  # в демо подписке лежит специальная картинка
#     )
#
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text=message_text.offer_subscription_text,
#         parse_mode=ParseMode.MARKDOWN,
#         reply_markup=InlineKeyboardMarkup(keyboard),
#     )


@log_journal
async def show_paid_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Если есть апдейт значит функция вызвана ботом, чтобы сообщить, что его подписка закончилась
    Иначе функция вызвана юзером нажатием кнопки
    :param update:
    :param context:
    :return:
    """
    if update.message:
        chat_id = update.effective_chat.id
        message = message_text.offer_subscription_text
        button_text = "⏩ Вернуться в меню"
    else:
        query = update.callback_query
        await query.answer()
        chat_id = query.from_user.id
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
        chat_id=chat_id,
        photo=open(
            str(settings.MEDIA_ROOT) + "/" + str(demo_sub.image_cover), "rb"
        ),  # в демо подписке лежит специальная картинка
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return BASE_STATES


@log_journal
async def preview_paid_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE, subscription_title=None):
    """
    Если в сообщении есть апдейт значит функция вызвана ботом при попытке пользователя записать вип
    голос без вип подписки
    Иначе эта функция вызвана юзером нажатием кнопки
    :param update:
    :param context:
    :param subscription_title:
    :return:
    """
    if update.message:
        title = subscription_title
    else:
        query = update.callback_query
        await query.answer()
        title = query.data.split("paid_subscription_")[1]

    subscription = await Subscription.objects.aget(title=title)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id if update.message else query.from_user.id,
        photo=open(
            str(settings.MEDIA_ROOT) + "/" + str(subscription.image_cover), "rb"
        ),
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id if update.message else query.from_user.id,
        text=message_text.offer_vip_subscription_text if update.message else subscription.description,
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
        status='waiting',
        user=user,
        subscription=subscription
    )

    logger.info(f'{order.id=}')
    data = {
        'subscription_title': subscription.telegram_title,
        'order_id': order.id,
        'amount': amount,
        'chat_id': chat_id
    }

    await push_amqp_message(data, routing_key='bot-to-payment')

    return BASE_STATES



from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import os

from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.models import Subscription
from bot.logic.utils import log_journal, get_object
from bot.logic import message_text
from bot.logic.constants import *


@log_journal
async def show_paid_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = list()
    async for sub in Subscription.objects.exclude(title=os.environ.get('DEFAULT_SUBSCRIPTION')).all():
        keyboard.append(
            [
                InlineKeyboardButton(sub.telegram_title, callback_data=f'paid_subscription_{sub.title}')
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton("⏩ Перейти к выбору голосов", callback_data='category_menu')
        ]
    )

    # await context.bot.delete_message(
    #     chat_id=query.message.chat.id,
    #     message_id=query.message.message_id
    # )

    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=open(str(settings.MEDIA_ROOT) + '/covers/all_paid_subs.png', 'rb'),
        # caption=message_text.all_paid_subs,
        # reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=message_text.all_paid_subs,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return BASE_STATES


@log_journal
async def preview_paid_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subscription_title = query.data.split('paid_subscription_')[1]
    subscription = await get_object(Subscription, title=subscription_title)
    #
    # await context.bot.delete_message(
    #     chat_id=query.message.chat.id,
    #     message_id=query.message.message_id
    # )

    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=open(str(settings.MEDIA_ROOT) + "/" + str(subscription.image_cover), 'rb'),
        # caption=subscription.description,
        # reply_markup=InlineKeyboardMarkup(
        #     [
        #         [
        #             InlineKeyboardButton(f" 💵 Разовый платёж - {subscription.price} руб",
        #                                  callback_data=f"payment_{subscription.price}")
        #         ],
        #         [
        #             InlineKeyboardButton("▶️ Другие подписки", callback_data='paid_subscriptions')
        #         ]
        #     ]
        # )
    )

    await context.bot.send_message(
    # await query.edit_message_text(
        chat_id=query.message.chat.id,
        text=subscription.description,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f" 💵 Разовый платёж - {subscription.price} руб", callback_data=f"payment_{subscription.price}")
                ],
                [
                    InlineKeyboardButton("▶️ Другие подписки", callback_data='paid_subscriptions')
                ]
            ]
        )
    )

    return BASE_STATES

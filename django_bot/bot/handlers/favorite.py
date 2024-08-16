import os
from uuid import uuid4
import django
import logging
from asgiref.sync import sync_to_async

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from bot.logic.utils import log_journal
from bot.logic.constants import *
from bot.logic import message_text


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from bot.models import Voice, Subscription
from user.models import User

logger = logging.getLogger(__name__)


@sync_to_async
def voice_add_favorite(model, arg):
    model.favorites.add(arg)
    return


@sync_to_async
def voice_remove_favorite(model, arg):
    model.favorites.remove(arg)
    return


@log_journal
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    slug_voice = query.data.split("favorite-add-")[1]

    voice = await Voice.objects.aget(slug=slug_voice)
    user = await User.objects.aget(telegram_id=query.from_user.id)

    await voice_add_favorite(user, voice)

    await query.edit_message_text(
        text=message_text.favorite_added.format(title=voice.title),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⏪ Вернуться в меню", callback_data="category_menu"
                    ),
                    InlineKeyboardButton("🔴Начать запись", callback_data="record"),
                ]
            ]
        ),
    )

    return BASE_STATES


@log_journal
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    slug_voice = query.data.split("favorite-remove-")[1]

    voice = await Voice.objects.aget(slug=slug_voice)
    user = await User.objects.aget(telegram_id=query.from_user.id)

    await voice_remove_favorite(user, voice)

    await query.edit_message_text(
        text=message_text.favorite_deleted.format(title=voice.title),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⏪ Вернуться в меню", callback_data="category_menu"
                    ),
                    InlineKeyboardButton("🔴Начать запись", callback_data="record"),
                ]
            ]
        ),
    )

    return BASE_STATES


@log_journal
async def roll_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    user = await User.objects.aget(telegram_id=update.inline_query.from_user.id)

    default_image = "https://img.freepik.com/free-photo/3d-rendering-hydraulic-elements_23-2149333332.jpg?t=st=1714904107~exp=1714907707~hmac=98d51596c9ad15af1086b0d1916f5567c1191255c42d157c87c59bab266d6e84&w=2000"
    results = []
    async for voice in user.favorites.all():
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=voice.title,
                description=voice.description,
                thumbnail_url=os.environ.get("GITHUB_HOST") + voice.image if voice.image else '',
                input_message_content=InputTextMessageContent(voice.slug),
            )
        )
    await update.inline_query.answer(results, cache_time=10, auto_pagination=True)
    return ConversationHandler.END

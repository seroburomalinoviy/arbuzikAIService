from uuid import uuid4
import os
import django
from dotenv import load_dotenv
import logging

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, ConversationHandler

from bot.logic.utils import log_journal
from bot.logic.constants import *


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from bot.models import Voice, Subscription

load_dotenv()


@log_journal
async def inline_searching(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Поиск по всем голосам
    :param update:
    :param context:
    :return:
    """
    query = update.inline_query
    if not query:
        return

    results = []
    async for voice in Voice.objects.filter(search_words__icontains=query.query):
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=voice.title,
                description=voice.description,
                thumbnail_url=os.environ.get("GITHUB_HOST") + voice.image,
                input_message_content=InputTextMessageContent(voice.slug),
            )
        )
    try:
        await query.answer(results, cache_time=300, auto_pagination=True)
    except:
        logging.warning('A voice did not get an image')
    return ConversationHandler.END

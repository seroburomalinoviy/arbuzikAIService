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

logger = logging.getLogger(__name__)

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
        logger.info(os.environ.get("GITHUB_HOST") + voice.image)
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=voice.title,
                description=voice.description,
                thumbnail_url=os.environ.get("GITHUB_HOST") + voice.image if voice.image else '',
                input_message_content=InputTextMessageContent(voice.slug),
            )
        )
    await query.answer(results, cache_time=1, auto_pagination=True)
    return ConversationHandler.END

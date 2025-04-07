from uuid import uuid4
import os
import django
from dotenv import load_dotenv
import logging
import traceback

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, ConversationHandler

from bot.logic.utils import log_journal, connection
from bot.logic.constants import *


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from bot.models import Voice, Subscription

logger = logging.getLogger(__name__)

load_dotenv()


@connection
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
    async for voice in Voice.objects.filter(search_words__icontains=query.query).exclude(subcategory__title="system"):
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
        logger.error(f'A voice did not get an icon, traceback: {traceback.format_exc()}')
    return ConversationHandler.END

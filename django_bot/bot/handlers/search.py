from uuid import uuid4
import os
import django

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, ConversationHandler

from bot.logic.utils import log_journal, get_object

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.models import Voice, Subscription, MediaData




@log_journal
async def inline_searching(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Поиск по всем голосам
    :param update:
    :param context:
    :return:
    """
    query = update.inline_query.query
    if not query:
        return

    user_subscription = await get_object(Subscription, users__telegram_id=update.inline_query.from_user.id)

    default_image = "https://img.freepik.com/free-photo/3d-rendering-hydraulic-elements_23-2149333332.jpg?t=st=1714904107~exp=1714907707~hmac=98d51596c9ad15af1086b0d1916f5567c1191255c42d157c87c59bab266d6e84&w=2000"
    results = []
    async for voice in Voice.objects.filter(subcategory__category__subscription=user_subscription,
                                            title=query):
        # voice_media_data = await get_object(MediaData, slug=voice.slug_voice)
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=voice.title,
                description=voice.description,
                # todo установить ssl сертификат
                thumbnail_url=default_image,  # str(settings.MEDIA_URL) + str(voice_media_data.image),
                input_message_content=InputTextMessageContent(voice.slug_voice)
            )
        )
    await update.inline_query.answer(results, cache_time=100, auto_pagination=True)
    return ConversationHandler.END

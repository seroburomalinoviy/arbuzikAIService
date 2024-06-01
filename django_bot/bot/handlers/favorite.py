import os
import django
import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.logic.utils import get_object, filter_objects, log_journal, save_model
from bot.logic.constants import *
from bot.logic import message_text


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.models import Voice
from user.models import User

logger = logging.getLogger(__name__)


@log_journal
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    slug_voice = query.data.split('favorite-add-')[1]

    voice = await get_object(Voice, slug_voice=slug_voice)
    user = await get_object(User, telegram_id=query.from_user.id)
    user.favorites.add(voice)

    await query.edit_message_text(
        text=message_text.format(title=voice.title),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⏪ Вернуться в меню', callback_data='category_menu'),
                    InlineKeyboardButton('🔴Начать запись', callback_data='record'),
                ]
            ]
        )
    )

    return BASE_STATES


@log_journal
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()



    return BASE_STATES
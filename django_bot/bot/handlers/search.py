from telegram import Update
from telegram.ext import ContextTypes

from bot.logic.utils import log_journal


@log_journal
async def search_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Поиск по всем голосам
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    await query.answer()
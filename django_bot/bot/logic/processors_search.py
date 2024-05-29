from telegram import Update
from telegram.ext import ContextTypes

from utils import log_journal


@log_journal
async def search_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
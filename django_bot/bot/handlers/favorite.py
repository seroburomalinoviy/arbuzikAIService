from telegram import Update
from telegram.ext import ContextTypes

from bot.logic.utils import get_object, filter_objects, log_journal, save_model
from bot.logic.constants import *

import logging

logger = logging.getLogger(__name__)


@log_journal
async def favorite_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()



    return BASE_STATES
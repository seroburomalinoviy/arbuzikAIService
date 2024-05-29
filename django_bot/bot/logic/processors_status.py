from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import log_journal
from constants import WAITING
import message_text
import keyboards


@log_journal
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Заглушка проверки состояния обработки запроса преобразования аудио нейросетью
    """
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=message_text.check_status_text,
        reply_markup=InlineKeyboardMarkup(keyboards.check_status)
    )
    return WAITING
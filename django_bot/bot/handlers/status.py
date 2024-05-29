from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.logic.utils import log_journal
from bot.logic.constants import START_ROUTES
from bot.logic import message_text
from bot.logic import keyboards


@log_journal
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Заглушка проверки состояния обработки запроса преобразования аудио нейросетью
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=message_text.check_status_text,
        reply_markup=InlineKeyboardMarkup(keyboards.check_status)
    )
    return START_ROUTES
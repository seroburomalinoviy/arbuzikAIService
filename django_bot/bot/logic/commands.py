import os
import logging
from dotenv import load_dotenv
from telegram.constants import ParseMode

from bot.structures.base_classes import BaseCommandHandler
from bot.logic import (message_text, keyboards)
from bot.logic.constants import *

from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, InlineKeyboardMarkup

load_dotenv()
logger = logging.getLogger(__name__)


class StartHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['processing_permission'] = False
        await update.message.reply_text(
            message_text.subscription_question,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription)
        )
        return BASE_STATES


class MenuHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            message_text.subscription_question,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription)
        )
        return BASE_STATES


class HelpHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            message_text.help_message,
            parse_mode=ParseMode.MARKDOWN
        )
        return BASE_STATES
        
        
class PitchHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class ProfileHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class CancelHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return ConversationHandler.END

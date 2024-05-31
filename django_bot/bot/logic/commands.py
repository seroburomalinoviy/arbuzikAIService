import os
import logging
from dotenv import load_dotenv
from ast import literal_eval

from bot.structures.base_classes import BaseCommandHandler
from bot.logic import (message_text, keyboards)
from bot.logic.constants import *

from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, InlineKeyboardMarkup

load_dotenv()
logger = logging.getLogger(__name__)


class StartHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            message_text.subscription_question,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription)
        )
        return BASE_STATES


class VoiceChangeHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class HelpHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class StatusHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...
        
        
class PitchHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class ProfileHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class MenuHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class CancelHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return ConversationHandler.END

import os
import logging
from dotenv import load_dotenv
from ast import literal_eval

from bot.structures.base_classes import BaseCommandHandler
from bot.logic import (message_text, keyboards)
from bot.logic.constants import (START_ROUTES, AUDIO)

from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, InlineKeyboardMarkup

load_dotenv()
logger = logging.getLogger(__name__)


class TestHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        admins = literal_eval(os.environ.get("ADMIN_IDS"))
        if update.effective_user.id in admins:
            await update.message.reply_text(
                "Send an audio file."
            )
            return AUDIO
        else:
            await update.message.reply_text(
                "Sorry, that's a test function."
            )


class StartHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            message_text.subscription_question,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription)
        )
        return START_ROUTES


class VoiceChangeHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class HelpHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class StatusHandler(BaseCommandHandler):
    def __init__(self) -> None:
        self._pattern = '^check_status$'
    
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        # TODO: Взаимодействие с очередью mqrabbit для получения статуса
        await query.edit_message_text(
            text=message_text.check_status_text, 
            reply_markup=InlineKeyboardMarkup(keyboards.check_status)
        )
        
    @property
    def pattern(self) -> str:
        return self._pattern
        


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

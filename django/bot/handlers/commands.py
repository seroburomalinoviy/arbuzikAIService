import os
import logging
from dotenv import load_dotenv
from ast import literal_eval

from django.bot.structures.base_classes import BaseCommandHandler
from django.bot.logic import messages, keyboards
from django.bot.logic.constants import (START_ROUTES, AUDIO)

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
            messages.subscription_question,
            reply_markup=InlineKeyboardMarkup(keyboards.subscription)
        )
        return START_ROUTES


class VoiceChangeHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class HelpHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class StatusHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

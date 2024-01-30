from bot.models.base_classes import BaseCommandHandler

from telegram.ext import ContextTypes
from telegram import Update

import os
from dotenv import load_dotenv
load_dotenv()


class TestHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id in os.environ.get('ADMIN_IDS'):



class VoiceChangeHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class StartHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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


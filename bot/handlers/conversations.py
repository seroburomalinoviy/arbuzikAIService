from bot.models.base_classes import BaseConversationHandler
from bot.handlers.commands import TestHandler, CancelHandler, get_audio, get_parameters
from bot.logic.constants import (
AUDIO, PARAMETRS
)

from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler




class TestConversationHandler(BaseConversationHandler):
    def entrypoints(self):
        return [CommandHandler("test", TestHandler())]

    def states(self):
        return {
            AUDIO: [MessageHandler(filters.ALL, get_audio)],
            PARAMETRS:[MessageHandler(filters.TEXT, get_parameters)]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]

from bot.structures.base_classes import BaseConversationHandler
from bot.handlers.commands import TestHandler, CancelHandler, StartHandler

from bot.logic import processors

from bot.logic.constants import (
AUDIO, PARAMETRS, START_ROUTES
)

from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler


class TestConversationHandler(BaseConversationHandler):
    def entrypoints(self):
        return [CommandHandler("test", TestHandler())]

    def states(self):
        return {
            AUDIO: [MessageHandler(filters.ALL, processors.get_audio)],
            PARAMETRS:[MessageHandler(filters.TEXT, processors.get_parameters)]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class MainConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [CommandHandler("start", StartHandler())]

    def states(self):
        return {
            START_ROUTES: [CallbackQueryHandler(processors.subscription, pattern="sub_0")]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]

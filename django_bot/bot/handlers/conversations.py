from bot.structures.base_classes import BaseConversationHandler
from bot.handlers.commands import TestHandler, CancelHandler, StartHandler

from bot.logic import processors
from bot.logic import message_text
from bot.logic.constants import (
AUDIO, PARAMETRS, START_ROUTES, END_ROUTES
)

from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, InlineQueryHandler


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
            START_ROUTES: [
                CallbackQueryHandler(processors.subscription, pattern="^subscription"),
                CallbackQueryHandler(processors.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(processors.search_all, pattern="^search_all$"),
                CallbackQueryHandler(processors.subcategory_menu, pattern="^category_"),
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class VoiceConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                    CallbackQueryHandler(processors.voice_set, pattern='^record_'),
                    CallbackQueryHandler(processors.category_menu, pattern='^category_menu'),
                    CallbackQueryHandler(processors.subcategory_menu, pattern='^category_'),
                    CallbackQueryHandler(processors.subcategory_menu, pattern='^favorite-add'),
            ]


    def states(self):
        return {
            START_ROUTES: [
                CallbackQueryHandler(processors.voice_set, pattern="^record_"),
                CallbackQueryHandler(processors.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(processors.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(processors.voice_preview, pattern="^voice_preview"),
            ]
        }

    def fallbacks(self):
        return [CallbackQueryHandler(processors.category_menu, pattern="^back_category$")]

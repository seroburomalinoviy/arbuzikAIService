from bot.structures.base_classes import BaseConversationHandler
from bot.logic.commands import CancelHandler, StartHandler, MenuHandler

from bot.handlers import main, search, paid_subscription, favorite
from bot.logic.constants import *

from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler

base_states = {
            BASE_STATES: [
                CallbackQueryHandler(main.subscription, pattern="^subscription"),
                CallbackQueryHandler(main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(main.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(search.search_all, pattern="^search_all$"),
                CallbackQueryHandler(paid_subscription.show_paid_subscriptions, pattern="^paid_subscriptions$"),
                CallbackQueryHandler(paid_subscription.preview_paid_subscription, pattern="^paid_subscription_"),
                CallbackQueryHandler(main.voice_set_0, pattern="^voice_set_0$"),
                CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_sub$"),
                CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_add$")
            ]
        }


class StartConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                CommandHandler("start", StartHandler()),
            ]

    def states(self):
        return base_states

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class MainConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                CommandHandler("menu", main.category_menu),
            ]

    def states(self):
        return base_states

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class VoiceConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                MessageHandler(filters.TEXT, main.voice_preview),
            ]

    def states(self):
        return base_states

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class AudioConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                MessageHandler(filters.VOICE & ~filters.COMMAND, main.voice_process),
                MessageHandler(filters.AUDIO & ~filters.COMMAND, main.audio_process)
        ]

    def states(self):
        return {
            WAITING:[
                CallbackQueryHandler(main.check_status, pattern='^check_status$')
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


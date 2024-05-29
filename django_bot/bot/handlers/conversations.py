from bot.structures.base_classes import BaseConversationHandler
from bot.handlers.commands import CancelHandler, StartHandler, MenuHandler

from bot.logic import processors
from bot.logic import processors_search
from bot.logic import processors_paid_subscription
from bot.logic import processors_status
from bot.logic.constants import (
AUDIO, PARAMETRS, START_ROUTES, WAITING, END_ROUTES
)

from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler


class MainConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [CommandHandler("start", StartHandler())]

    def states(self):
        return {
            START_ROUTES: [
                CallbackQueryHandler(processors.subscription, pattern="^subscription"),
                CallbackQueryHandler(processors.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(processors_search.search_all, pattern="^search_all$"),
                CallbackQueryHandler(processors.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(processors_paid_subscription.show_paid_subscriptions, pattern="^paid_subscriptions$"),
                CallbackQueryHandler(processors_paid_subscription.preview_paid_subscription, pattern="^paid_subscription_"),
                CommandHandler('menu', processors.category_menu)
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class VoiceConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [MessageHandler(filters.TEXT, processors.voice_preview)]


    def states(self):
        return {
            START_ROUTES: [
                # MessageHandler(filters.TEXT, processors.voice_preview),
                CallbackQueryHandler(processors.voice_set, pattern="^record$"),
                CallbackQueryHandler(processors.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(processors.voice_preview, pattern="^voice_preview$"),
                CallbackQueryHandler(processors.voice_set_0, pattern="^voice_set_0$"),
                CallbackQueryHandler(processors.pitch_setting, pattern="^voice_set_sub$"),
                CallbackQueryHandler(processors.pitch_setting, pattern="^voice_set_add$"),
                CommandHandler('menu', processors.category_menu)
            ]
        }

    def fallbacks(self):
        # todo: try change on cancel handler command
        return [CallbackQueryHandler(processors.category_menu, pattern="^back_category$")]


class AudioConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                MessageHandler(filters.VOICE & ~filters.COMMAND, processors.voice_process),
                MessageHandler(filters.AUDIO & ~filters.COMMAND, processors.audio_process)
        ]

    def states(self):
        return {
            WAITING: [
                CallbackQueryHandler(processors_status.check_status, pattern='^check_status$')
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


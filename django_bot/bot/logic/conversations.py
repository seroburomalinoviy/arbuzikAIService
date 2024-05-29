from bot.structures.base_classes import BaseConversationHandler
from bot.logic.commands import CancelHandler, StartHandler, MenuHandler

from bot.handlers import handlers_main
from bot.handlers import handlers_search
from bot.handlers import handlers_paid_subscription
from bot.handlers import handlers_status
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
                CallbackQueryHandler(handlers_main.subscription, pattern="^subscription"),
                CallbackQueryHandler(handlers_main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(handlers_search.search_all, pattern="^search_all$"),
                CallbackQueryHandler(handlers_main.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(handlers_paid_subscription.show_paid_subscriptions, pattern="^paid_subscriptions$"),
                CallbackQueryHandler(handlers_paid_subscription.preview_paid_subscription, pattern="^paid_subscription_"),
                CommandHandler('menu', handlers_main.category_menu)
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class VoiceConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [MessageHandler(filters.TEXT, handlers_main.voice_preview)]


    def states(self):
        return {
            START_ROUTES: [
                # MessageHandler(filters.TEXT, processors.voice_preview),
                CallbackQueryHandler(handlers_main.voice_set, pattern="^record"),
                CallbackQueryHandler(handlers_main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(handlers_main.voice_preview, pattern="^voice_preview$"),
                CallbackQueryHandler(handlers_main.voice_set_0, pattern="^voice_set_0$"),
                CallbackQueryHandler(handlers_main.pitch_setting, pattern="^voice_set_sub$"),
                CallbackQueryHandler(handlers_main.pitch_setting, pattern="^voice_set_add$"),
                # CommandHandler('menu', handlers_main.category_menu)
            ]
        }

    def fallbacks(self):
        # todo: try change on cancel handler command
        return [CallbackQueryHandler(handlers_main.category_menu, pattern="^back_category$")]


class AudioConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                MessageHandler(filters.VOICE & ~filters.COMMAND, handlers_main.voice_process),
                MessageHandler(filters.AUDIO & ~filters.COMMAND, handlers_main.audio_process)
        ]

    def states(self):
        return {
            WAITING: [
                CallbackQueryHandler(handlers_status.check_status, pattern='^check_status$')
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


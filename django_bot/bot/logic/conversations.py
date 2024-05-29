from bot.structures.base_classes import BaseConversationHandler
from bot.logic.commands import CancelHandler, StartHandler, MenuHandler

from bot import handlers
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
                CallbackQueryHandler(handlers.main.subscription, pattern="^subscription"),
                CallbackQueryHandler(handlers.main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(handlers.search.search_all, pattern="^search_all$"),
                CallbackQueryHandler(handlers.main.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(handlers.paid_subscription.show_paid_subscriptions, pattern="^paid_subscriptions$"),
                CallbackQueryHandler(handlers.paid_subscription.preview_paid_subscription, pattern="^paid_subscription_"),
                CommandHandler('menu', handlers.main.category_menu)
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class VoiceConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [MessageHandler(filters.TEXT, handlers.main.voice_preview)]


    def states(self):
        return {
            START_ROUTES: [
                # MessageHandler(filters.TEXT, processors.voice_preview),
                CallbackQueryHandler(handlers.main.voice_set, pattern="^record"),
                CallbackQueryHandler(handlers.main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(handlers.main.voice_preview, pattern="^voice_preview$"),
                CallbackQueryHandler(handlers.main.voice_set_0, pattern="^voice_set_0$"),
                CallbackQueryHandler(handlers.main.pitch_setting, pattern="^voice_set_sub$"),
                CallbackQueryHandler(handlers.main.pitch_setting, pattern="^voice_set_add$"),
                # CommandHandler('menu', handlers_main.category_menu)
            ]
        }

    def fallbacks(self):
        # todo: try change on cancel handler command
        return [CallbackQueryHandler(handlers.main.category_menu, pattern="^back_category$")]


class AudioConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                MessageHandler(filters.VOICE & ~filters.COMMAND, handlers.main.voice_process),
                MessageHandler(filters.AUDIO & ~filters.COMMAND, handlers.main.audio_process)
        ]

    def states(self):
        return {
            WAITING: [
                CallbackQueryHandler(handlers.status.check_status, pattern='^check_status$')
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


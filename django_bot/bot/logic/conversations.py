from bot.structures.base_classes import BaseConversationHandler
from bot.logic.commands import CancelHandler, StartHandler, MenuHandler

from bot.handlers import main, search, paid_subscription, status, favorite
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
                CallbackQueryHandler(main.subscription, pattern="^subscription"),
                CallbackQueryHandler(main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(search.search_all, pattern="^search_all$"),
                CallbackQueryHandler(main.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(paid_subscription.show_paid_subscriptions, pattern="^paid_subscriptions$"),
                CallbackQueryHandler(paid_subscription.preview_paid_subscription, pattern="^paid_subscription_"),
                # CallbackQueryHandler(main.voice_set, pattern="^record"),
                CommandHandler('menu', main.category_menu)
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


class VoiceConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [MessageHandler(filters.TEXT, main.voice_preview)]


    def states(self):
        return {
            START_ROUTES: [
                # MessageHandler(filters.TEXT, main.voice_preview),
                CallbackQueryHandler(main.voice_set, pattern="^record"),
                # CallbackQueryHandler(main.category_menu, pattern="^category_menu$"),
                # CallbackQueryHandler(main.voice_preview, pattern="^voice_preview$"),
                CallbackQueryHandler(main.voice_set_0, pattern="^voice_set_0$"),
                CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_sub$"),
                CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_add$"),
                # CommandHandler('menu', main.category_menu)
            ]
        }

    def fallbacks(self):
        # todo: try change on cancel handler command
        return [CallbackQueryHandler(main.category_menu, pattern="^back_category$")]


class AudioConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                MessageHandler(filters.VOICE & ~filters.COMMAND, main.voice_process),
                MessageHandler(filters.AUDIO & ~filters.COMMAND, main.audio_process)
        ]

    def states(self):
        return {
            WAITING: [
                CallbackQueryHandler(status.check_status, pattern='^check_status$')
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]


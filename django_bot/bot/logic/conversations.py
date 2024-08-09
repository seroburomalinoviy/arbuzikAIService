from bot.structures.base_classes import BaseConversationHandler
from bot.logic.commands import CancelHandler, StartHandler, MenuHandler, HelpHandler

from bot.handlers import main, search, paid_subscription, favorite
from bot.logic.constants import *

from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler


class MainConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                CommandHandler("start", StartHandler()),
                CommandHandler("help", HelpHandler()),
                CommandHandler("menu", main.category_menu),
                MessageHandler((filters.AUDIO | filters.VOICE) & ~filters.COMMAND, main.voice_audio_process),
                MessageHandler(filters.TEXT, main.voice_preview)
            ]

    def states(self):
        return {
            BASE_STATES: [
                CallbackQueryHandler(main.subscription, pattern="^subscription"),
                CallbackQueryHandler(main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(main.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(paid_subscription.show_paid_subscriptions, pattern="^paid_subscriptions$"),
                CallbackQueryHandler(paid_subscription.preview_paid_subscription, pattern="^paid_subscription_"),
                CallbackQueryHandler(main.voice_set, pattern="^record$"),
                CallbackQueryHandler(main.voice_set_0, pattern="^voice_set_0$"),
                CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_sub$"),
                CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_add$"),
                CallbackQueryHandler(favorite.add, pattern="^favorite-add-"),
                CallbackQueryHandler(favorite.remove, pattern="^favorite-remove-"),
                CallbackQueryHandler(main.check_status, pattern='^check_status$')
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]

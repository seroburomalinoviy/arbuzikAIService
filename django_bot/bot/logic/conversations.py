from bot.structures.base_classes import BaseConversationHandler
from bot.logic.commands import CancelHandler, StartHandler, MenuHandler

from bot.handlers import main, search, paid_subscription, favorite
from bot.logic.constants import *

from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler

nested_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.VOICE & ~filters.COMMAND, main.voice_process),
        MessageHandler(filters.AUDIO & ~filters.COMMAND, main.audio_process),
    ],
    states={
        SETUP_VOICE:[
            CallbackQueryHandler(main.voice_set_0, pattern="^voice_set_0$"),
            CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_sub$"),
            CallbackQueryHandler(main.pitch_setting, pattern="^voice_set_add$")
        ],
        WAITING: [
            CallbackQueryHandler(main.check_status, pattern='^check_status$')
        ]
    },
    fallbacks=[CommandHandler("cancel", CancelHandler())],
    map_to_parent={
        END: BASE_STATES
    }
)



class MainConversationHandler(BaseConversationHandler):

    def entrypoints(self):
        return [
                CommandHandler("start", StartHandler()),
                CommandHandler("menu", main.category_menu),

                MessageHandler(filters.TEXT, main.voice_preview)
            ]

    def states(self):
        return {
            BASE_STATES: [
                CallbackQueryHandler(main.subscription, pattern="^subscription"),
                CallbackQueryHandler(main.category_menu, pattern="^category_menu$"),
                CallbackQueryHandler(main.subcategory_menu, pattern="^category_"),
                CallbackQueryHandler(search.search_all, pattern="^search_all$"),
                CallbackQueryHandler(paid_subscription.show_paid_subscriptions, pattern="^paid_subscriptions$"),
                CallbackQueryHandler(paid_subscription.preview_paid_subscription, pattern="^paid_subscription_"),
                CallbackQueryHandler(main.voice_set, pattern="^record$"),
            ],
             VOICE_PROCESS: [
                 nested_conv
            ]
        }

    def fallbacks(self):
        return [CommandHandler("cancel", CancelHandler())]

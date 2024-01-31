import telegram.ext as tg_ext
from bot.handlers.conversations import TestConversationHandler


def init_handlers(application: tg_ext.Application):
    convers = TestConversationHandler()

    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=convers.entrypoints(),
            states=convers.states(),
            fallbacks=convers.fallbacks()
        )
    )

    return application
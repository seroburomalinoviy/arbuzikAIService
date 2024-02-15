import telegram.ext as tg_ext
from django.bot.handlers.conversations import TestConversationHandler, MainConversationHandler


def init_handlers(application: tg_ext.Application):
    test = TestConversationHandler()
    main = MainConversationHandler()

    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=test.entrypoints(),
            states=test.states(),
            fallbacks=test.fallbacks()
        )
    )

    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=main.entrypoints(),
            states=main.states(),
            fallbacks=main.fallbacks()
        )
    )

    return application
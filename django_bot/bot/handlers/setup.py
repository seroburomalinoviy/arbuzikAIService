import telegram.ext as tg_ext
from bot.handlers.conversations import TestConversationHandler, MainConversationHandler
from bot.logic.processors import inline_query


def init_handlers(application: tg_ext.Application):
    test = TestConversationHandler()
    main = MainConversationHandler()
    # inline_mode = inline_query

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

    # application.add_handler(
    #     tg_ext.InlineQueryHandler(inline_mode)
    # )

    return application
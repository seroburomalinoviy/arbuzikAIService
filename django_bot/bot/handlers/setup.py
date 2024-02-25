import telegram.ext as tg_ext
from bot.handlers.conversations import TestConversationHandler, MainConversationHandler, VoiceConversationHandler
from bot.logic.processors import inline_query


def init_handlers(application: tg_ext.Application):
    test = TestConversationHandler()
    main = MainConversationHandler()
    voice = VoiceConversationHandler()
    inline_mode = inline_query

    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=test.entrypoints(),
            states=test.states(),
            fallbacks=test.fallbacks()
        )
    )

    # application.add_handler(
    #     tg_ext.ConversationHandler(
    #         entry_points=voice.entrypoints(),
    #         states=voice.states(),
    #         fallbacks=voice.fallbacks()
    #     )
    # )

    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=main.entrypoints(),
            states=main.states(),
            fallbacks=main.fallbacks(),
            allow_reentry=True
        )
    )

    application.add_handler(
        tg_ext.InlineQueryHandler(inline_mode)
    )

    return application
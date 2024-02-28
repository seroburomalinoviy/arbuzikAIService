import telegram.ext as tg_ext
from bot.handlers.conversations import TestConversationHandler, MainConversationHandler, VoiceConversationHandler
from bot.logic.processors import inline_query
from telegram import Update

import logging

logger = logging.getLogger(__name__)


async def on_result_chosen(update: Update, context: tg_ext.ContextTypes.DEFAULT_TYPE):
    result = update.chosen_inline_result.query
    context.user_data['inline_query'] = result
    logger.info(result)


def init_handlers(application: tg_ext.Application):
    test = TestConversationHandler()
    main = MainConversationHandler()
    voice = VoiceConversationHandler()

    # Test
    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=test.entrypoints(),
            states=test.states(),
            fallbacks=test.fallbacks()
        )
    )

    # Main
    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=main.entrypoints(),
            states=main.states(),
            fallbacks=main.fallbacks(),
            allow_reentry=True
        )
    )

    # Inline
    application.add_handler(tg_ext.InlineQueryHandler(inline_query))

    # ChosenInlineResult
    # application.add_handler(tg_ext.ChosenInlineResultHandler(on_result_chosen))

    # Voice
    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=voice.entrypoints(),
            states=voice.states(),
            fallbacks=main.fallbacks()
        )
    )

    return application
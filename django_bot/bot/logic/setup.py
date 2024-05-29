import telegram.ext as tg_ext
from bot.logic.conversations import (
    MainConversationHandler,
    VoiceConversationHandler, AudioConversationHandler
)

from bot.handlers.main import inline_query
from telegram import Update

import logging

logger = logging.getLogger(__name__)


async def on_result_chosen(update: Update, context: tg_ext.ContextTypes.DEFAULT_TYPE):
    result = update.chosen_inline_result.query
    context.user_data['inline_query'] = result
    logger.info(result)


def init_handlers(application: tg_ext.Application):
    main = MainConversationHandler()
    voice = VoiceConversationHandler()
    audio = AudioConversationHandler()

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

    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=audio.entrypoints(),
            states=audio.states(),
            fallbacks=audio.fallbacks(),
        )
    )

    return application

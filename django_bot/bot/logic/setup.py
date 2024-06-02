import telegram.ext as tg_ext
from telegram import Update

from bot.handlers.main import voice_inline_query
from bot.handlers import search
from bot.handlers import favorite
from bot.logic.conversations import (
    MainConversationHandler,
)

import logging

logger = logging.getLogger(__name__)


async def on_result_chosen(update: Update, context: tg_ext.ContextTypes.DEFAULT_TYPE):
    result = update.chosen_inline_result.query
    context.user_data['inline_query'] = result
    logger.info(result)


def init_handlers(application: tg_ext.Application):
    main = MainConversationHandler()

    # Main
    application.add_handler(
        tg_ext.ConversationHandler(
            entry_points=main.entrypoints(),
            states=main.states(),
            fallbacks=main.fallbacks(),
            allow_reentry=True
        )
    )

    # Inline for favorites
    application.add_handler(tg_ext.InlineQueryHandler(favorite.roll_out, pattern='^favorites$'))

    # Inline for Voice
    application.add_handler(tg_ext.InlineQueryHandler(voice_inline_query, pattern='^sub_'))

    # Inline for search
    application.add_handler(tg_ext.InlineQueryHandler(search.inline_searching))

    # ChosenInlineResult
    # application.add_handler(tg_ext.ChosenInlineResultHandler(on_result_chosen))

    return application

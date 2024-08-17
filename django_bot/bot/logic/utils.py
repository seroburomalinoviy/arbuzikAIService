from datetime import datetime
from zoneinfo import ZoneInfo
from django.conf import settings
import functools
from telegram import Update
import logging

logger = logging.getLogger(__name__)


def get_moscow_time() -> datetime:
    return datetime.now(tz=ZoneInfo(settings.TIME_ZONE))


def log_journal(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update: Update = args[0]
        if update.message:
            _id = str(update.effective_user.id)
        elif update.callback_query:
            _id = str(update.callback_query.from_user.id)
        elif update.inline_query:
            _id = str(update.inline_query.from_user.id)
        else:
            _id = "Not found"

        logger.info(
            f"JOURNAL: {func.__name__} - was called for user - {_id} - tg_id"
        )
        return await func(*args, **kwargs)

    return wrapper

import logging
import os
from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder

from bot.handlers.setup import init_handlers

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s >>> %(funcName)s(%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    TOKEN = os.environ.get('BOT_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()

    application = init_handlers(application)

    application.run_polling()


if "__main__" == __name__:
    main()

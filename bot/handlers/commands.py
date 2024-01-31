from bot.models.base_classes import BaseCommandHandler
from bot.logic.constants import (
AUDIO, PARAMETRS
)

from telegram.ext import ContextTypes, ConversationHandler, CommandHandler
from telegram import Update

import os
import pika
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


async def get_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = await update.message.effective_attachment.get_file()
    filename = f'audio_file_{update.message.from_user.id}.ogg'
    await audio.download_to_drive(filename)
    logger.info('file downloaded')

    context.user_data['path_to_file'] = filename

    await update.message.reply_text(
        f"File is downloaded and named as`{filename}`\nSend a parameters."
    )
    return PARAMETRS


async def get_parameters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parameters = update.message.text
    logger.info(f'{parameters=}')
    filename = context.user_data['path_to_file']
    logger.info(f'{filename=}')
    command = f'{filename} {parameters}'

    await update.message.reply_text(
        f"The command I collected:\n\n{command}\n\nStart script ..."
    )

    # start script

    # установка соединения
    _parameters = pika.URLParameters(
        'amqp: // rabbit_user: rabbit_password @ host:port / vhost'
        )
    connection = pika.BlockingConnection(_parameters)
    channel = connection.channel()

    # публикация
    channel.basic_publish(exchange='test_exchange', routing_key='test_key', body=bytes(command))

    # закрыть соединение
    connection.close()

    return ConversationHandler.END


class TestHandler(BaseCommandHandler):
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Send an audio file."
        )
        return AUDIO


class VoiceChangeHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class StartHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class HelpHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class StatusHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class PitchHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class ProfileHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class MenuHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ...


class CancelHandler(BaseCommandHandler):
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return ConversationHandler.END

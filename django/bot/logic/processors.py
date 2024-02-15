import pika
import logging
from dotenv import load_dotenv
import os

from django.bot.logic.constants import (
    PARAMETRS, START_ROUTES
)
from django.bot.logic import messages, keyboards

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

load_dotenv()
logger = logging.getLogger(__name__)

allowed_user_statuses = ['member', 'creator', 'administrator']
unresolved_user_statuses = ['kicked', 'restricted', 'left']


async def subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_member = await context.bot.get_chat_member(
        chat_id=os.environ.get('CHANNEL_ID'),
        user_id=update.effective_user.id
    )
    logger.info(f'User {is_member.user} is {is_member.status}')

    query = update.callback_query
    await query.answer()
    if is_member.status in allowed_user_statuses:


        await query.message.reply_text(
            messages.menu,
            reply_markup=InlineKeyboardMarkup(keyboards.categories)
        )
        return START_ROUTES
    elif is_member.status in unresolved_user_statuses:
        await query.message.reply_text(
            messages.subscription_check,
            reply_markup=InlineKeyboardMarkup(keyboards.subscription)
        )


# for TestHandler
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

    credentials = pika.PlainCredentials(
        os.environ.get('RABBIT_USER'),
        os.environ.get('RABBIT_PASSWORD'))
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            os.environ.get('RABBIT_HOST'),
            int(os.environ.get('RABBIT_PORT')
            ),
        '/', credentials, heartbeat=0, socket_timeout=7)
    )
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=f'{command}')
    connection.close()

    return ConversationHandler.END




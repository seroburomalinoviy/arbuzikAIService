import logging
from dotenv import load_dotenv
import os
import asyncstdlib as a

from bot.logic import message_text, keyboards
from bot.amqp_driver import push_amqp_message
from bot.logic.constants import (
    PARAMETRS, START_ROUTES
)

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from asgiref.sync import sync_to_async

from bot.models import Voice, Category, Subcategory

load_dotenv()
logger = logging.getLogger(__name__)

allowed_user_statuses = ['member', 'creator', 'administrator']
unresolved_user_statuses = ['kicked', 'restricted', 'left']


@sync_to_async
def get_objects(model) -> list:
    return list(model.objects.all())


@sync_to_async
def get_object_by_id(model, _id: int):
    return model.objects.get(id=_id)


@sync_to_async
def filter_subcategories(model, _id: int) -> list:
    return list(model.objects.filter(category_id=_id))


# STEP_0 - SUBSCRIPTION
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
            message_text.demo_rights,
            reply_markup=InlineKeyboardMarkup(keyboards.is_subscribed)
        )
        return START_ROUTES
    elif is_member.status in unresolved_user_statuses:
        await query.message.reply_text(
            message_text.subscription_check,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription)
        )
        return START_ROUTES


# STEP_2 - CATEGORY_MENU
async def category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categories = await get_objects(Category)
    len_cat = len(categories)

    keyboard = [keyboards.search_all_voices]  # add button
    async for i, _ in a.enumerate(categories[0:int(len_cat/2)]):
        keyboard.append(
            [
                InlineKeyboardButton(categories[i].title,
                                     callback_data='category_' + str(categories[i].id)),
                InlineKeyboardButton(categories[int(len_cat/2)+i].title,
                                     callback_data='category_' + str(categories[int(len_cat/2)+i].id))
            ]
        )
    if len_cat % 2 != 0:
        keyboard.append([InlineKeyboardButton(categories[len_cat - 1].title,
                                              callback_data='subcategory_' + str(categories[len_cat - 1].id))])

    await query.message.reply_text(
            message_text.category_menu,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return START_ROUTES


async def subcategory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split('category_')[1])
    category = await get_object_by_id(Category, category_id)
    subcategories = await filter_subcategories(Subcategory, category_id)

    len_subc = len(subcategories)
    keyboard = []
    async for i, _ in a.enumerate(subcategories[0:int(len_subc/2)]):
        keyboard.append(
            [
                InlineKeyboardButton(subcategories[i].title,
                                     callback_data='subcategory_' + str(subcategories[i].id)),
                InlineKeyboardButton(subcategories[int(len_subc/2)+i].title,
                                     callback_data='subcategory_' + str(subcategories[int(len_subc/2)+i].id))
            ]
        )
    keyboard.append(keyboards.back_to_category)  # add button

    await query.message.reply_text(
        category.title + '\n' + category.description,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def search_all():
    pass


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
    filename = context.user_data.get('path_to_file')
    logger.info(f'{filename=}')
    command = f'{filename} {parameters}'

    await update.message.reply_text(
        f"The command I collected:\n\n{command}\n\nStart script ..."
    )

    await push_amqp_message('privet')

    return ConversationHandler.END




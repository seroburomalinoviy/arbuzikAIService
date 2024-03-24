from pathlib import Path
import logging
from dotenv import load_dotenv
import os
import asyncstdlib as a
from uuid import uuid4
from asgiref.sync import sync_to_async
import django

from bot.logic import message_text, keyboards
from bot.amqp_driver import push_amqp_message
from bot.logic.constants import (
    PARAMETRS, START_ROUTES, END_ROUTES
)

from telegram import (Update, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle,
                      InputTextMessageContent, InlineQueryResultsButton)
from telegram.ext import ContextTypes, ConversationHandler


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from bot.models import Voice, Category, Subcategory

load_dotenv()
logger = logging.getLogger(__name__)

allowed_user_statuses = ['member', 'creator', 'administrator']
unresolved_user_statuses = ['kicked', 'restricted', 'left']


@sync_to_async
def get_all_objects(model) -> list:
    return list(model.objects.all())


@sync_to_async
def get_object(model, **kwargs):
    return model.objects.get(**kwargs)


@sync_to_async
def filter_objects(model, **kwargs) -> list:
    return list(model.objects.filter(**kwargs))


# STEP_0 - SUBSCRIPTION
async def subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_member = await context.bot.get_chat_member(
        chat_id=os.environ.get('CHANNEL_ID'),
        user_id=update.effective_user.id
    )
    logger.info(f'User {is_member.user} is {is_member.status}')

    query = update.callback_query

    if is_member.status in allowed_user_statuses:
        await query.answer()
        await query.edit_message_text(
            message_text.demo_rights,
            reply_markup=InlineKeyboardMarkup(keyboards.is_subscribed)
        )
        return START_ROUTES
    elif is_member.status in unresolved_user_statuses:
        await query.answer(text='Сначала подпишись :)')
        await update.message.reply_text(
            message_text.subscription_check,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription)
        )
        return START_ROUTES


# STEP_2 - CATEGORY_MENU
async def category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categories = await get_all_objects(Category)
    len_cat = len(categories)

    keyboard = [keyboards.search_all_voices]  # add button
    async for i, _ in a.enumerate(categories[0:int(len_cat / 2)]):

        keyboard.append(
            [
                InlineKeyboardButton(categories[i].title,
                                     callback_data='category_' + str(categories[i].id)
                                     ),
                InlineKeyboardButton(categories[int(len_cat / 2) + i].title,
                                     callback_data='category_' + str(categories[int(len_cat / 2) + i].id)
                                    )
            ]
        )

    if len_cat % 2 != 0:
        keyboard.append([InlineKeyboardButton(categories[len_cat - 1].title,
                                              callback_data='category_' + str(categories[len_cat - 1].id)
                                              )
                         ])

    await query.edit_message_text(
        message_text.category_menu,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return START_ROUTES


# STEP_3 - SUBCATEGORY_MENU
async def subcategory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split('category_')[1])
    subcategories = await filter_objects(Subcategory, category_id=category_id)

    len_subc = len(subcategories)
    keyboard = []
    async for i, _ in a.enumerate(subcategories[0:int(len_subc / 2)]):
        keyboard.append(
            [
                InlineKeyboardButton(subcategories[i].title,
                                     switch_inline_query_current_chat=subcategories[i].slug,
                                     ),
                InlineKeyboardButton(subcategories[int(len_subc / 2) + i].title,
                                     switch_inline_query_current_chat=subcategories[int(len_subc / 2) + i].slug,
                                     )
            ]
        )
    if len_subc % 2 != 0:
        keyboard.append(
            [
                InlineKeyboardButton(subcategories[len_subc - 1].title,
                                     switch_inline_query_current_chat=subcategories[len_subc - 1].slug,
                                     )
            ]
        )
    keyboard.append(keyboards.category_menu)  # add button

    category = await get_object(Category, id=category_id)
    await query.edit_message_text(
        category.title + '\n' + category.description,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return START_ROUTES


# INLINE_MODE - QUERY
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    slug = update.inline_query.query
    if not slug:
        return

    context.user_data['slug'] = slug
    voices = await filter_objects(Voice, subcategory__slug=slug)


    # todo: проверка голоса в избранном, в зависимости от этого отдавать кнопку избранное/удалить из избранного

    results = []
    async for num, voice in a.enumerate(voices):
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=voice.title,
                description=voice.description,
                thumbnail_url="https://img.icons8.com/2266EE/search",
                input_message_content=InputTextMessageContent(voice.title)
            )
        )
    await update.inline_query.answer(results, cache_time=1, auto_pagination=True)
    return ConversationHandler.END


async def voice_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        context.user_data['voice_title'] = update.message.text
        if context.user_data.get(f'pitch_{update.message.text}'):
            pass
        else:
            context.user_data[f'pitch_{update.message.text}'] = 0

    await update.message.reply_text(
        message_text.voice_preview,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⏪ Вернуться в меню', callback_data='category_menu'),
                    InlineKeyboardButton('🔴Начать запись', callback_data="record"),

                ],
                [
                    InlineKeyboardButton('⭐ В избранное', callback_data="favorite-add"),
                ]
            ]
        )
    )
    return START_ROUTES


async def voice_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    voice_title = context.user_data.get('voice_title')
    pitch = context.user_data.get(f'pitch_{voice_title}') if context.user_data.get(f'pitch_{voice_title}') else "0"

    await query.edit_message_text(
        message_text.voice_set.format(name=voice_title),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('-1', callback_data='voice_set_sub'),
                    InlineKeyboardButton(str(pitch), callback_data='voice_set_0'),
                    InlineKeyboardButton('+1', callback_data='voice_set_add'),
                ],
                [
                    InlineKeyboardButton('⏪ Вернуться в меню', callback_data='category_menu')
                ]
            ]
        )
    )
    return START_ROUTES


async def voice_set_0(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    voice_title = context.user_data.get('voice_title')
    pitch = context.user_data.get(f'pitch_{voice_title}') if context.user_data.get(f'pitch_{voice_title}') else "0"
    await query.answer(f'Тональность {pitch}')
    return START_ROUTES


async def pitch_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    voice_title = context.user_data.get('voice_title')

    if query.data == 'voice_set_sub':
        context.user_data[f'pitch_{voice_title}'] -= 1
    elif query.data == 'voice_set_add':
        context.user_data[f'pitch_{voice_title}'] += 1

    pitch = str(context.user_data.get(f'pitch_{voice_title}'))

    await query.edit_message_text(
        message_text.voice_set.format(name=voice_title),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('-1', callback_data='voice_set_sub'),
                    InlineKeyboardButton(pitch, callback_data='voice_set_0'),
                    InlineKeyboardButton('+1', callback_data='voice_set_add'),
                ],
                [
                    InlineKeyboardButton('⏪ Вернуться в меню', callback_data='category_menu')
                ]
            ]
        )
    )
    return START_ROUTES


async def voice_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = await update.message.voice.get_file()  # get voice file from user
    user_id = str(update.message.from_user.id)
    voice_volume = os.environ.get('USER_VOICES_RAW_VOLUME')  # path to volume for raw voice file
    extension = '.ogg'
    voice_filename = user_id  # raw voice file name
    voice_path = Path(voice_volume + '/' + voice_filename + extension)
    voice_title = context.user_data.get('voice_title')
    pitch = context.user_data.get(f'pitch_{voice_title}')
    voice_obj = await get_object(Voice, title=voice_title)
    voice_model_pth = voice_obj.model_pth.FieldFile.name.split('/')[1]
    voice_model_index = voice_obj.model_index.FieldFile.name.split('/')[1]

    await voice.download_to_drive(custom_path=voice_path)  # download voice file to host
    logger.info(f'The voice file with name {user_id} downloaded to {voice_path}')

    await update.message.reply_text(
        message_text.conversation_end,
        reply_markup=InlineKeyboardMarkup(keyboards.check_status)
    )

    payload = f"{voice_filename}__{pitch}__{voice_model_pth}__{voice_model_index}__{extension}"

    await push_amqp_message(payload)
    # todo: write to db




async def audio_process():
    pass


async def search_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


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

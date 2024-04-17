from pathlib import Path
import logging
from dotenv import load_dotenv
import os
import asyncstdlib as a
from uuid import uuid4
from asgiref.sync import sync_to_async
import django
from django.db import models
import json
from datetime import datetime
from zoneinfo import ZoneInfo

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
from bot.models import Voice, Category, Subcategory, Subscription, User

load_dotenv()
logger = logging.getLogger(__name__)

allowed_user_statuses = ['member', 'creator', 'administrator']
unresolved_user_statuses = ['kicked', 'restricted', 'left']


def get_moscow_time() -> datetime: # мб выделить в отдельный файл, как и функци работы с базой данных
    return datetime.now(tz=ZoneInfo('Europe/Moscow')) # втавить глобальную переменую из env


@sync_to_async
def get_all_objects(model:models.Model) -> list:
    return list(model.objects.all())


@sync_to_async
def get_object(model:models.Model, **kwargs) -> models.Model: 
    return model.objects.get(**kwargs)


@sync_to_async
def filter_objects(model:models.Model, **kwargs) -> list:
    return list(model.objects.filter(**kwargs))


@sync_to_async
def save_model(model:models.Model) -> None:
    return model.save()


@sync_to_async
def get_or_create_objets(model:models.Model, **kwargs) -> models.Model:
    return model.objects.get_or_create(**kwargs)


async def set_demo_to_user(user_model:User, demo_subsrctiption:Subscription, 
                           tg_user_name, tg_nick_name) -> None:
    # TODO: проверить инициализацию юзера
    # нужно ли выставлять subscription_final_date??
    user_model.subscription_status = True
    user_model.subscription = demo_subsrctiption 
    user_model.user_name=tg_user_name,
    user_model.nick_name=tg_nick_name
    user_model.subscription_count_attpemps = demo_subsrctiption.days_limit 
    # user_model.subscription_final_date = get_moscow_time() #???
    await save_model(user_model)


@sync_to_async
def check_subsсrtiption(user_model:User, demo_subsсrctiption:Subscription) -> None:
    user_subsrctiption = user_model.subscription
    actual_subscription = user_subsrctiption
    actual_status = user_model.subscription_status
    current_date = get_moscow_time()
    if user_model.subscription_count_attpemps == 0 and \
        user_model.subscription_final_date < current_date and \
            actual_status == True:
        # если подписки все закончились  и Actual status True обнляем
        actual_status = False
        actual_subscription = demo_subsсrctiption
        user_model.subscription_status = actual_status
        user_model.subscription = actual_subscription
        user_model.subscription_count_attpemps = 0
        save_model(user_model)
    
    return actual_subscription


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
    tg_user_id = str(update.effective_user.id)
    tg_user_name = update.effective_user.username
    tg_nick_name = update.effective_user.first_name
    demo_subsrctiption: Subscription = await get_object(Subscription, title='demo')# вставить глобальную переменную названия баозовой подписки
    user, created = await get_or_create_objets(User, telegram_id=tg_user_id)
    
    if created: 
        await set_demo_to_user(user, demo_subsrctiption, tg_user_name, tg_nick_name)
        user_subsrctiption = demo_subsrctiption
    else:
        user_subsrctiption = await check_subsсrtiption(user, demo_subsrctiption)
    # key = str(uuid4())    
    context.user_data['subs'] = user_subsrctiption
    query = update.callback_query
    await query.answer()
    categories = await filter_objects(Category,
                                      available_subscriptions=user_subsrctiption)
    len_cat = len(categories)

    keyboard = [keyboards.search_all_voices]  # add button
    async for i, _ in a.enumerate(categories[0:int(len_cat / 2)]):
        logger.info(f'callback_data = {"category_" + str(categories[i].id)}')
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
    current_category_id = int(query.data.split('category_')[1])
    user_subscription = context.user_data.get('subs')
    subcategories = await filter_objects(Subcategory, category_id=current_category_id, 
                                         available_subscriptions=user_subscription)# добавить допом фильтр подписки

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

    category = await get_object(Category, id=current_category_id)
    await query.edit_message_text(
        category.title + '\n' + category.description,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return START_ROUTES


# INLINE_MODE - QUERY
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slug = update.inline_query.query
    if not slug:
        return
    user_subscription = context.user_data['subs']
    context.user_data['slug'] = slug #why??
    voices = await filter_objects(Voice, subcategory__slug=slug, 
                                  available_subscriptions=user_subscription)


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
    chat_id = str(update.message.chat.id)
    extension = '.ogg'
    voice_title = context.user_data.get('voice_title')
    voice_filename = voice_title + '_' + str(uuid4()) + extension  # raw voice file name
    voice_path = Path(os.environ.get('USER_VOICES_RAW_VOLUME') + '/' + voice_filename)
    pitch = context.user_data.get(f'pitch_{voice_title}')
    voice_obj = await get_object(Voice, title=voice_title)
    voice_model_pth = voice_obj.model_pth.name.split('/')[1]
    voice_model_index = voice_obj.model_index.name.split('/')[1]

    await voice.download_to_drive(custom_path=voice_path)  # download voice file to host
    logger.info(f'The voice file with name {user_id} downloaded to {voice_path}')

    await update.message.reply_text(
        message_text.conversation_end,
        reply_markup=InlineKeyboardMarkup(keyboards.check_status)
    )
    payload = {
        "user_id": user_id,
        "chat_id": chat_id,
        "voice_filename": voice_filename,
        "pitch": pitch,
        "voice_model_pth": voice_model_pth,
        "voice_model_index": voice_model_index,
    }

    await push_amqp_message(json.dumps(payload))
    # todo: write to db

    return ConversationHandler.END




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

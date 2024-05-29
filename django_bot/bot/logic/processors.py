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
from django.conf import settings

from bot.logic import message_text, keyboards
from bot.amqp_driver import push_amqp_message
from bot.logic.constants import (
    PARAMETRS, START_ROUTES, END_ROUTES, WAITING
)

from telegram import (Update, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle,
                      InputTextMessageContent, InlineQueryResultsButton)
from telegram.ext import ContextTypes, ConversationHandler


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.models import Voice, Category, Subcategory, Subscription, MediaData
from user.models import User

load_dotenv()
logger = logging.getLogger(__name__)

allowed_user_statuses = ['member', 'creator', 'administrator']
unresolved_user_statuses = ['kicked', 'restricted', 'left']


def get_moscow_time() -> datetime:
    return datetime.now(tz=ZoneInfo(settings.TIME_ZONE))


@sync_to_async
def get_all_objects(model: models.Model) -> list:
    return list(model.objects.all())


@sync_to_async
def get_object(model: models.Model, **kwargs):
    return model.objects.get(**kwargs)


@sync_to_async
def filter_objects(model: models.Model, **kwargs) -> list:
    return list(model.objects.filter(**kwargs))


@sync_to_async
def save_model(model: models.Model) -> None:
    return model.save()


@sync_to_async
def get_or_create_objets(model: models.Model, **kwargs):
    return model.objects.get_or_create(**kwargs)


async def subscription_list():
    return


async def set_demo_to_user(user_model: User, tg_user_name, tg_nick_name) -> None:
    demo_subscription: Subscription = await get_object(Subscription, title=os.environ.get('DEFAULT_SUBSCRIPTION'))
    current_date = get_moscow_time()

    user_model.subscription_status = True
    user_model.subscription = demo_subscription
    user_model.telegram_username = tg_user_name
    user_model.telegram_nickname = tg_nick_name
    user_model.subscription_attempts = demo_subscription.days_limit
    user_model.subscription_final_date = current_date

    await save_model(user_model)
    
    return user_model.subscription.title


@sync_to_async
def check_subscription(user_model: User) -> tuple[str, bool]:
    """
    Деактивирует подписку пользователя, если у него нет ни одной активной подписки
    :param user_model:
    :return:
    """
    actual_status = user_model.subscription_status
    current_date = get_moscow_time()
    if (
        user_model.subscription_attempts == 0 and
        user_model.subscription_final_date < current_date and
        actual_status
        ):
        user_model.subscription = Subscription.objects.get(title=os.environ.get('DEFAULT_SUBSCRIPTION'))
        user_model.subscription_status = False
        user_model.save()
    
    return user_model.subscription.title, user_model.subscription_status


# STEP_0 - SUBSCRIPTION
async def subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_member = await context.bot.get_chat_member(
        chat_id=os.environ.get('CHANNEL_ID'),
        user_id=update.effective_user.id
    )
    logger.debug(f'User {is_member.user} is {is_member.status}')

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
    if not update.message:
        tg_user_id = str(update.callback_query.from_user.id)
        tg_user_name = update.callback_query.from_user.username
        tg_nick_name = update.callback_query.from_user.first_name
    else:
        tg_user_id = str(update.effective_user.id)
        tg_user_name = update.effective_user.username
        tg_nick_name = update.effective_user.first_name

    user, user_created = await get_or_create_objets(User, telegram_id=tg_user_id)
    if user_created:
        subscription_name = await set_demo_to_user(user, tg_user_name, tg_nick_name)
        subscription_status = True
    else:
        subscription_name, subscription_status = await check_subscription(user)

    context.user_data['subscription_name'] = subscription_name
    context.user_data['subscription_status'] = subscription_status

    categories = await filter_objects(Category,
                                      subscription__title=subscription_name)
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

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            message_text.category_menu,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            message_text.category_menu,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    return START_ROUTES


# STEP_3 - SUBCATEGORY_MENU
async def subcategory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current_category_id = int(query.data.split('category_')[1])
    context.user_data['current_category_id'] = current_category_id

    subcategories = await filter_objects(Subcategory, category__id=current_category_id)

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
    subscription_name = context.user_data['subscription_name']

    slug_subcategory = update.inline_query.query
    if not slug_subcategory:
        return
    context.user_data['slug_subcategory'] = slug_subcategory

    current_category_id = context.user_data['current_category_id']

    default_image = "https://img.icons8.com/2266EE/search"
    default_image = "https://img.freepik.com/free-photo/3d-rendering-hydraulic-elements_23-2149333332.jpg?t=st=1714904107~exp=1714907707~hmac=98d51596c9ad15af1086b0d1916f5567c1191255c42d157c87c59bab266d6e84&w=2000"
    results = []
    async for voice in Voice.objects.filter(
            subcategory__category__id=current_category_id,
            subcategory__slug=slug_subcategory,
            subcategory__category__subscription__title=subscription_name
    ):
        voice_media_data = await get_object(MediaData, slug=voice.slug_voice)
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=voice.title,
                description=voice.description,
                # todo установить ssl сертификат
                thumbnail_url=default_image, #str(settings.MEDIA_URL) + str(voice_media_data.image),
                input_message_content=InputTextMessageContent(voice.slug_voice)
            )
        )
    await update.inline_query.answer(results, cache_time=100, auto_pagination=True)
    return ConversationHandler.END


async def voice_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    1. Проверяем пользвоательскую подписку (todo: вынести в отдельную функцию)
    2. Отпрваляем демку и превью Voice'a
    :param update:
    :param context:
    :return:
    """
    user = await get_object(User, telegram_id=update.effective_user.id)
    context.user_data['subscription_name'], context.user_data['subscription_status'] = await check_subscription(user)

    if context.user_data.get('subscription_status'):
        if context.user_data['subscription_name'] == os.environ.get('DEFAULT_SUBSCRIPTION'):
            user.subscription_attempts -= 1
            if user.subscription_attempts <= 0:
                user.subscription_status = False
                await save_model(user)
            await save_model(user)

        else:
            if user.subscription_final_date < get_moscow_time():
                user.subscription_status = False
                await save_model(user)

    user = await get_object(User, telegram_id=update.effective_user.id)
    if not user.subscription_status:
        await update.message.reply_text(
            message_text.subscription_finished,
            reply_markup=InlineKeyboardMarkup(keyboards.is_subscribed)
        )
        return ConversationHandler.END

    # if update.message: # todo ест ли случаи когда нет update.message ?
    slug_voice = update.message.text
    context.user_data['slug_voice'] = slug_voice

    if context.user_data.get(f'pitch_{update.message.text}'):
        pass
    else:
        context.user_data[f'pitch_{update.message.text}'] = 0

    # todo: проверка голоса в избранном, в зависимости от этого отдавать кнопку избранное/удалить из избранного
    favorite_voices = []
    try:
        favorite_voices = await filter_objects(User, favorites__slug_voice=slug_voice)
    except Exception as e:
        logger.info(f'{e}')

    logger.info(f'{favorite_voices=}')

    voice_media_data = await get_object(MediaData, slug=slug_voice)
    demka_path = voice_media_data.demka.path

    try:
        await update.message.reply_audio(
            audio=open(demka_path, 'rb')
        )
    except Exception as e:
        logger.warning(e)
        await update.message.reply_text(
            'Запись демонстрации голоса в работе'
        )

    await update.message.reply_text(
        message_text.voice_preview,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⏪ Вернуться в меню', callback_data='category_menu'),
                    InlineKeyboardButton('🔴Начать запись', callback_data="record"),

                ],
                [
                    InlineKeyboardButton('⭐ В избранное' if favorite_voices else 'Удалить из избранного', callback_data="favorite-add"),
                ]
            ]
        )
    )
    return START_ROUTES


async def voice_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    slug_voice = context.user_data.get('slug_voice')
    pitch = context.user_data.get(f'pitch_{slug_voice}') if context.user_data.get(f'pitch_{slug_voice}') else "0"

    await query.edit_message_text(
        message_text.voice_set.format(name=slug_voice),
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
    slug_voice = context.user_data.get('slug_voice')
    pitch = context.user_data.get(f'pitch_{slug_voice}') if context.user_data.get(f'pitch_{slug_voice}') else "0"
    await query.answer(f'Тональность {pitch}')
    return START_ROUTES


async def pitch_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    slug_voice = context.user_data.get('slug_voice')

    if query.data == 'voice_set_sub':
        context.user_data[f'pitch_{slug_voice}'] -= 1
    elif query.data == 'voice_set_add':
        context.user_data[f'pitch_{slug_voice}'] += 1

    pitch = str(context.user_data.get(f'pitch_{slug_voice}'))



    await query.edit_message_text(
        message_text.voice_set.format(name=slug_voice),
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
    slug_voice = context.user_data.get('slug_voice')
    # current_category_id = context.user_data.get('current_category_id')
    voice_filename = slug_voice + '_' + str(uuid4()) + extension  # raw voice file name
    voice_path = Path(os.environ.get('USER_VOICES_RAW_VOLUME') + '/' + voice_filename)
    pitch = context.user_data.get(f'pitch_{slug_voice}')

    slug = context.user_data.get('slug_voice')
    voice_media_data: MediaData = await get_object(MediaData, slug=slug)
    voice_model_pth = str(voice_media_data.model_pth)
    voice_model_index = str(voice_media_data.model_index)

    logger.info(f'\n\nvoice_model_pth = {voice_model_pth}')
    logger.info(f'voice_model_index = {voice_model_index}\n\n')

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

    return WAITING




async def audio_process():
    pass


async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Заглушка проверки состояния обработки запроса преобразования аудио нейросетью
    """
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
            text=message_text.check_status_text, 
            reply_markup=InlineKeyboardMarkup(keyboards.check_status)
        )
    return WAITING


async def search_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


async def show_paid_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = list()
    async for sub in Subscription.objects.exclude(title=os.environ.get('DEFAULT_SUBSCRIPTION')).all():
        keyboard.append(
            [
                InlineKeyboardButton(sub.telegram_title, callback_data=f'paid_subscription_{sub.title}')
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton("⏩ Перейти к выбору голосов", callback_data='category_menu')
        ]
    )

    # await context.bot.delete_message(
    #     chat_id=query.message.chat.id,
    #     message_id=query.message.message_id
    # )

    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=open(str(settings.MEDIA_ROOT) + '/covers/all_paid_subs.png', 'rb'),
        # caption=message_text.all_paid_subs,
        # reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=message_text.all_paid_subs,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return START_ROUTES


async def preview_paid_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subscription_title = query.data.split('paid_subscription_')[1]
    subscription = await get_object(Subscription, title=subscription_title)
    #
    # await context.bot.delete_message(
    #     chat_id=query.message.chat.id,
    #     message_id=query.message.message_id
    # )

    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=open(str(settings.MEDIA_ROOT) + "/" + str(subscription.image_cover), 'rb'),
        # caption=subscription.description,
        # reply_markup=InlineKeyboardMarkup(
        #     [
        #         [
        #             InlineKeyboardButton(f" 💵 Разовый платёж - {subscription.price} руб",
        #                                  callback_data=f"payment_{subscription.price}")
        #         ],
        #         [
        #             InlineKeyboardButton("▶️ Другие подписки", callback_data='paid_subscriptions')
        #         ]
        #     ]
        # )
    )

    await context.bot.send_message(
    # await query.edit_message_text(
        chat_id=query.message.chat.id,
        text=subscription.description,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f" 💵 Разовый платёж - {subscription.price} руб", callback_data=f"payment_{subscription.price}")
                ],
                [
                    InlineKeyboardButton("▶️ Другие подписки", callback_data='paid_subscriptions')
                ]
            ]
        )
    )

    return START_ROUTES




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

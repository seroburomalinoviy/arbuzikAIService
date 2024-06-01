from pathlib import Path
import logging
from dotenv import load_dotenv
import os
import asyncstdlib as a
from uuid import uuid4
from asgiref.sync import sync_to_async
import django
import json

from bot.logic import message_text, keyboards
from bot.logic.amqp_driver import push_amqp_message
from bot.logic.constants import *
from bot.logic.utils import (get_moscow_time, log_journal, save_model, get_object,
                   get_or_create_objets, filter_objects)


from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, ApplicationHandlerStop
from telegram import (Update, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle,
                      InputTextMessageContent, InlineQueryResultsButton)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.models import Voice, Category, Subcategory, Subscription, MediaData
from user.models import User

logger = logging.getLogger(__name__)


load_dotenv()

allowed_user_statuses = ['member', 'creator', 'administrator']
unresolved_user_statuses = ['kicked', 'restricted', 'left']


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
    Отстреливатель пользователей
    1. Деактивирует подписку пользователя, если у него нет ни одной активной подписки
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


@log_journal
async def subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Подписка на канал
    1. Проверяем подписан ли пользователь на канал арбузика
    :param update:
    :param context:
    :return:
    """
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
        return BASE_STATES
    elif is_member.status in unresolved_user_statuses:
        await query.answer(text='Сначала подпишись :)')
        await update.message.reply_text(
            message_text.subscription_check,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription)
        )
        return BASE_STATES


@log_journal
async def category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Главное меню / Категории
    1. Создаем или получаем пользователя в бд
    2. Получаем параметры подписки пользователя
    3. Отравляем пользователю категории в соответствии с его подпиской
    :param update:
    :param context:
    :return:
    """
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
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            message_text.category_menu,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )

    return BASE_STATES


@log_journal
async def subcategory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Подкатегории
    1. Отправляем подкатегории в соответствии с подпиской пользователя
    :param update:
    :param context:
    :return:
    """
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
    # category menu button
    keyboard.append(keyboards.category_menu)

    category = await get_object(Category, id=current_category_id)
    await query.edit_message_text(
        f'<strong>{category.title}</strong>\n{category.description}',
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

    return BASE_STATES


@log_journal
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Меню выбора голосов
    :param update:
    :param context:
    :return:
    """
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
    # await context.bot.answer_inline_query(update.inline_query.id, results)
    return ConversationHandler.END


@log_journal
async def voice_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Превью голоса
    1. Проверяем подписку (todo: вынести в отдельную функцию)
    2. проверяем избранные голоса пользователя
    3. Отправляем демку
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

    # Ограничение на количество символов - безопасность
    slug_voice = update.message.text[0:50]
    context.user_data['slug_voice'] = slug_voice

    if not context.user_data.get(f'pitch_{update.message.text}'):
        context.user_data[f'pitch_{update.message.text}'] = 0

    favorite_voices = []
    try:
        favorite_voices = await filter_objects(User, favorites__slug_voice=slug_voice)
    except Exception as e:
        logger.warning(f'{e}')

    button_favorite = ('⭐ В избранное', f'favorite-add-{slug_voice}')
    for voice in favorite_voices:
        if slug_voice in voice.slug_voice:
            button_favorite = ('Удалить из избранного', f'favorite-remove-{slug_voice}')

    try:
        voice_media_data = await get_object(MediaData, slug=slug_voice)
    except Exception as e:
        logger.warning(f'Voice {slug_voice} DOES NOT EXIST: {e}')
        await update.message.reply_text(
            text='Такой модели не существует попробуйте еще раз',
            reply_markup=InlineKeyboardMarkup(keyboards.is_subscribed)
        )
        return BASE_STATES

    demka_path = voice_media_data.demka.path

    try:
        await update.message.reply_audio(
            audio=open(demka_path, 'rb')
        )
    except Exception as e:
        logger.warning(e)
        await update.message.reply_text(
            'Демонстрация голоса в работе'
        )

    await update.message.reply_text(
        message_text.voice_preview,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⏪ Вернуться в меню', callback_data='category_menu'),
                    InlineKeyboardButton('🔴Начать запись', callback_data='record'),

                ],
                [
                    InlineKeyboardButton(button_favorite[0], callback_data=button_favorite[1]),
                ]
            ]
        )
    )
    return BASE_STATES


@log_journal
async def voice_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Представление голоса
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    await query.answer()

    slug_voice = context.user_data.get('slug_voice')
    pitch = context.user_data.get(f'pitch_{slug_voice}') if context.user_data.get(f'pitch_{slug_voice}') else "0"

    await query.edit_message_text(
        message_text.voice_set.format(name=slug_voice),
        parse_mode=ParseMode.HTML,
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
    return BASE_STATES


@log_journal
async def voice_set_0(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обнуление тональности
    1. Выводим плашку с обновленным значением тональности
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    slug_voice = context.user_data.get('slug_voice')
    pitch = context.user_data.get(f'pitch_{slug_voice}') if context.user_data.get(f'pitch_{slug_voice}') else "0"
    await query.answer(f'Тональность {pitch}')

    return BASE_STATES


@log_journal
async def pitch_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Настройка тональности
    1. Меняем значение тональности
    2. Сохраняем обновленное значение в кеш
    3. Возвращаем представление голоса с обновленным значением тональности
    :param update:
    :param context:
    :return:
    """
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
        parse_mode=ParseMode.HTML,
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
    return BASE_STATES


@log_journal
async def voice_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Захват голосового сообщения
    1. Получаем голосовое сообщение, данные пользователя и тональность голоса
    2. Сохраняем файл с голосовым сообщением
    3. Отправляем пользователю статус
    4. Отправляем данные в брокер сообщений
    :param update:
    :param context:
    :return:
    """
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
    voice_model_pth = str(voice_media_data.model_pth).split('models/')[1]
    voice_model_index = str(voice_media_data.model_index).split('models/')[1]

    logger.debug(f'{voice_model_pth=}')
    logger.debug(f'{voice_model_index=}')

    await voice.download_to_drive(custom_path=voice_path)  # download voice file to host
    logger.info(f'JOURNAL: Voice {slug_voice} downloaded to {voice_path} for user - {user_id} - tg_id')

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

    await update.message.reply_text(
        message_text.conversation_end,
        reply_markup=InlineKeyboardMarkup(keyboards.check_status)
    )

    return WAITING


@log_journal
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Заглушка проверки состояния обработки запроса преобразования аудио нейросетью
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    await query.answer('Еще в работе')

    await query.edit_message_text(
        text=message_text.check_status_text,
        reply_markup=InlineKeyboardMarkup(keyboards.check_status)
    )
    return WAITING


@log_journal
async def audio_process():
    pass





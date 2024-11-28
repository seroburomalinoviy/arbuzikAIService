from dotenv import load_dotenv
import os
from uuid import uuid4
from asgiref.sync import sync_to_async
import django
import logging

from bot.logic import message_text, keyboards
from bot.logic.amqp_driver import push_amqp_message
from bot.logic.constants import *
from bot.logic.utils import get_moscow_time, log_journal
from bot.handlers.paid_subscription import preview_paid_subscription, show_paid_subscriptions
from bot.structures.schemas import RVCData
from bot.structures.base_classes import PreparedFile


from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, ApplicationHandlerStop
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from bot.models import Voice, Category, Subcategory, Subscription
from user.models import User

load_dotenv()

allowed_user_statuses = ["member", "creator", "administrator"]
unresolved_user_statuses = ["kicked", "restricted", "left"]


async def set_demo_to_user(user: User, update: Update) -> None:
    demo_subscription: Subscription = await Subscription.objects.aget(
        title=os.environ.get("DEFAULT_SUBSCRIPTION")
    )

    user.subscription_status = True
    user.subscription = demo_subscription
    user.telegram_username = (
        update.effective_user.username
        if update.message
        else update.callback_query.from_user.username
    )
    user.telegram_nickname = (
        update.effective_user.first_name
        if update.message
        else update.callback_query.from_user.first_name
    )
    user.subscription_attempts = demo_subscription.days_limit

    await user.asave()


async def update_subscription(user: User):
    demo = os.environ.get("DEFAULT_SUBSCRIPTION")
    if user.subscription.title == demo:
        user.subscription_attempts -= 1
        await user.asave()


def is_valid_subscription(user: User) -> bool:
    demo = os.environ.get("DEFAULT_SUBSCRIPTION")
    if not user.subscription_status:
        return False
    else:
        if user.subscription.title == demo:
            if user.subscription_attempts <= 0:
                return False
            else:
                return True
        else:
            if user.subscription_final_date < get_moscow_time():
                return False
            else:
                return True


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
        user_model.subscription_attempts == 0
        and user_model.subscription_final_date < current_date
        and actual_status
    ):
        user_model.subscription = Subscription.objects.get(
            title=os.environ.get("DEFAULT_SUBSCRIPTION")
        )
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
        chat_id=os.environ.get("CHANNEL_ID"), user_id=update.effective_user.id
    )
    logging.debug(f"User {is_member.user} is {is_member.status}")

    query = update.callback_query

    if is_member.status in allowed_user_statuses:
        await query.answer()
        system_voice = await Voice.objects.aget(slug=os.environ.get('SYSTEM_VOICE'))
        demka_path = system_voice.demka.path
        demka_cover = system_voice.demka_image.path
        if os.path.exists(demka_path):
            if os.path.exists(demka_cover):
                await context.bot.send_audio(
                    chat_id=query.from_user.id,
                    audio=open(demka_path, "rb"),
                    filename=system_voice.title,
                    thumbnail=open(demka_cover, 'rb'),
                    duration=60
                )
            else:
                await context.bot.send_audio(
                    chat_id=query.from_user.id,
                    audio=open(demka_path, "rb"),
                    filename=system_voice.title,
                    duration=60
                )

        await query.edit_message_text(
            message_text.demo_rights,
            reply_markup=InlineKeyboardMarkup(keyboards.is_subscribed),
        )

        return BASE_STATES
    elif is_member.status in unresolved_user_statuses:
        await query.answer(text="Сначала подпишись :)")
        await update.message.reply_text(
            message_text.subscription_check,
            reply_markup=InlineKeyboardMarkup(keyboards.check_subscription),
        )
        return BASE_STATES


@log_journal
async def category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Главное меню / Категории
    1. Обновляем права на отправку голосовых
    2. Добавляем пользователя в бд и подписываем на демо
    3. Отравляем категории
    :param update:
    :param context:
    :return:
    """
    context.user_data["processing_permission"] = False

    tg_user_id = (
        str(update.effective_user.id)
        if update.message
        else str(update.callback_query.from_user.id)
    )

    user, user_created = await User.objects.aget_or_create(telegram_id=tg_user_id)
    if user_created:
        await set_demo_to_user(user, update)

    # Кнопки Поиск по всем голосам и Избранное
    keyboard = [keyboards.search_all_voices, keyboards.favorites]
    i = 0
    row = []
    async for category in Category.objects.exclude(title=os.environ.get('SYSTEM_VOICE')).exclude(title='VIP голоса').all().order_by('title').values("title", "id"):
        i += 1
        row.append(
            InlineKeyboardButton(
                category["title"], callback_data="category_" + str(category["id"])
            )
        )
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    vip_category = await Category.objects.aget(title='VIP голоса')
    keyboard.append(
            [InlineKeyboardButton(vip_category.title, callback_data="category_" + str(vip_category.id))]
    )

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            message_text.category_menu,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            message_text.category_menu,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
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
    current_category_id = int(query.data.split("category_")[1])
    context.user_data["current_category_id"] = current_category_id

    keyboard, row = [], []
    i = 0
    async for subcategory in Subcategory.objects.exclude(title=os.environ.get('SYSTEM_VOICE')).filter(
        category__id=current_category_id
    ).values("title", "slug"):
        i += 1
        row.append(
            InlineKeyboardButton(
                subcategory["title"],
                switch_inline_query_current_chat="sub_" + subcategory["slug"],
            )
        )
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # category menu button
    keyboard.append(keyboards.category_menu)

    category = await Category.objects.aget(id=current_category_id)
    await query.edit_message_text(
        f"<strong>{category.title}</strong>\n{category.description}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML,
    )

    return BASE_STATES


@log_journal
async def voice_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Меню выбора голосов
    :param update:
    :param context:
    :return:
    """

    slug_subcategory = update.inline_query.query.split("sub_")[1]
    if not slug_subcategory:
        logging.error("Slug of subcategory is empty")
        return
    context.user_data["slug_subcategory"] = slug_subcategory

    results = []
    async for voice in Voice.objects.filter(
        subcategory__slug=slug_subcategory,
    ):
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=voice.title,
                description=voice.description,
                thumbnail_url=os.environ.get("GITHUB_HOST") + voice.image,
                input_message_content=InputTextMessageContent(voice.slug),
            )
        )
    await update.inline_query.answer(results, cache_time=300, auto_pagination=True)
    return ConversationHandler.END


@log_journal
async def voice_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Превью голоса
    1. Отправляем демку
    2. Преднастраиваем pitch
    3. Проверяем избранные голоса

    :param update:
    :param context:
    :return:
    """
    slug_voice = update.message.text
    context.user_data["slug_voice"] = slug_voice

    if not await Voice.objects.filter(slug=slug_voice).acount():
        await update.message.reply_text(
            text="Такой модели не существует попробуйте еще раз",
            reply_markup=InlineKeyboardMarkup(keyboards.is_subscribed),
        )
        return BASE_STATES

    voice = await Voice.objects.aget(slug=slug_voice)
    context.user_data["voice_title"] = voice.title
    demka_path = voice.demka.path
    demka_image_path = voice.demka_image.path

    if not os.path.exists(demka_path):
        await update.message.reply_text("Демонстрация голоса в работе")
    else:
        if not os.path.exists(demka_image_path):
            await update.message.reply_audio(
                audio=open(demka_path, "rb"),
                filename=voice.title,
            )
        else:
            await update.message.reply_audio(
                audio=open(demka_path, "rb"),
                filename=voice.title,
                thumbnail=open(demka_image_path, 'rb')
            )

    if not context.user_data.get(f"pitch_{update.message.text}"):
        context.user_data[f"pitch_{update.message.text}"] = 0

    button_favorite = ("⭐ В избранное", f"favorite-add-{slug_voice}")
    async for voice in Voice.objects.filter(user__favorites__slug=slug_voice):
        if slug_voice in voice.slug:
            button_favorite = ("Удалить из избранного", f"favorite-remove-{slug_voice}")

    await update.message.reply_text(
        message_text.voice_preview,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⏪ Вернуться в меню", callback_data="category_menu"
                    ),
                    InlineKeyboardButton("🔴Начать запись", callback_data="record"),
                ],
                [
                    InlineKeyboardButton(
                        button_favorite[0], callback_data=button_favorite[1]
                    ),
                ],
            ]
        ),
    )
    return BASE_STATES


@log_journal
async def voice_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Представление голоса

    1. Проверка подписки
    2. Разрешаем отправлять аудио
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    await query.answer()

    user = await User.objects.select_related("subscription").aget(
        telegram_id=query.from_user.id
    )

    if not is_valid_subscription(user):
        user.subscription_status = False
        await user.asave()
        await show_paid_subscriptions(update, context, offer=True)
        return BASE_STATES

    slug_voice = context.user_data.get("slug_voice")

    if not await Subscription.objects.filter(
        voice__slug=slug_voice, title=user.subscription.title
    ).acount():
        await preview_paid_subscription(update, context, subscription_title='violetvip', offer=True)
        return BASE_STATES

    context.user_data["processing_permission"] = True

    pitch = (
        context.user_data.get(f"pitch_{slug_voice}")
        if context.user_data.get(f"pitch_{slug_voice}")
        else "0"
    )
    voice_title = context.user_data.get("voice_title")
    await query.edit_message_text(
        message_text.voice_set.format(name=voice_title),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("-1", callback_data="voice_set_sub"),
                    InlineKeyboardButton(str(pitch), callback_data="voice_set_0"),
                    InlineKeyboardButton("+1", callback_data="voice_set_add"),
                ],
                [
                    InlineKeyboardButton(
                        "⏪ Вернуться в меню", callback_data="category_menu"
                    )
                ],
            ]
        ),
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
    slug_voice = context.user_data.get("slug_voice")
    pitch = (
        context.user_data.get(f"pitch_{slug_voice}")
        if context.user_data.get(f"pitch_{slug_voice}")
        else "0"
    )
    await query.answer(f"Тональность {pitch}")

    return BASE_STATES


@log_journal
async def pitch_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Настройка тональности
    1. Меняем тональность
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    await query.answer()

    slug_voice = context.user_data.get("slug_voice")
    voice_title = context.user_data.get("voice_title")
    pitch = context.user_data.get(f"pitch_{slug_voice}")

    if query.data == "voice_set_sub":
        pitch_next = pitch - 1 if pitch > -TONE_LIMIT else pitch
    elif query.data == "voice_set_add":
        pitch_next = pitch + 1 if pitch < TONE_LIMIT else pitch

    context.user_data[f"pitch_{slug_voice}"] = pitch_next

    if not pitch_next == pitch:
        await query.edit_message_text(
            message_text.voice_set.format(name=voice_title),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("-1", callback_data="voice_set_sub"),
                        InlineKeyboardButton(pitch_next, callback_data="voice_set_0"),
                        InlineKeyboardButton("+1", callback_data="voice_set_add"),
                    ],
                    [
                        InlineKeyboardButton(
                            "⏪ Вернуться в меню", callback_data="category_menu"
                        )
                    ],
                ]
            ),
        )
    return BASE_STATES


@log_journal
async def voice_audio_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Захват голосового сообщения
    1. Проверяем права на отправку голосового
    2. Получаем голосовое сообщение, данные пользователя и тональность голоса
    3. Сохраняем файл с голосовым сообщением
    4. Отправляем пользователю статус
    5. Отправляем данные в брокер сообщений
    6. Обновляем подписку
    :param update:
    :param context:
    :return:
    """
    permission = context.user_data.get("processing_permission")
    if not permission:
        await update.message.reply_text(
            message_text.audio_permission_denied,
            reply_markup=InlineKeyboardMarkup(keyboards.is_subscribed),
        )
        return BASE_STATES

    user = await User.objects.select_related("subscription").aget(
        telegram_id=update.effective_user.id
    )
    if not is_valid_subscription(user):
        user.subscription_status = False
        await user.asave()
        await show_paid_subscriptions(update, context, offer=True)
        return BASE_STATES

    file = PreparedFile(update, context, user)

    if file is None:
        logging.error(f"неизвестный тип входного файла: {update.message.to_dict(recursive=True)}")
        await update.message.reply_text(
            text="Неизвестный тип входного файла. Попробуйте еще раз"
        )
        return BASE_STATES

    if not await file.is_valid_size():
        await update.message.reply_text(
            message_text.too_heavy_file
        )
        return BASE_STATES

    await file.calculate_duration()
    await file.download()

    slug_voice = context.user_data.get("slug_voice")
    voice = await Voice.objects.aget(slug=slug_voice)
    voice_model_pth = str(voice.model_pth).split("/")[-1]
    voice_model_index = str(voice.model_index).split("/")[-1]

    pitch = context.user_data.get(f"pitch_{slug_voice}")
    user_id = str(update.message.from_user.id)
    chat_id = str(update.message.chat.id)

    message = await update.message.reply_text(
        message_text.conversation_end,
        reply_markup=InlineKeyboardMarkup(keyboards.check_status),
    )
    payload = RVCData(
        duration=file.duration,
        voice_title=voice.title,
        user_id=user_id,
        chat_id=chat_id,
        voice_name=file.name,
        extension=file.extension,
        pitch=pitch,
        voice_model_index=voice_model_index,
        voice_model_pth=voice_model_pth,
        message_id=message.id
    )
    logging.info(f"{payload.model_dump()=}")

    await push_amqp_message(payload.model_dump(), routing_key="bot-to-rvc")

    await update_subscription(user)

    return BASE_STATES


@log_journal
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Заглушка проверки состояния обработки запроса преобразования аудио нейросетью
    :param update:
    :param context:
    :return:
    """
    query = update.callback_query
    await query.answer("Еще в работе")
    return BASE_STATES

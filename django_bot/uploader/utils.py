import os

import pandas as pd
import csv
from bot.models import Subscription, Category, Subcategory, Voice, MediaData


def subscription_parser(filepath):
    def get_reverse_dict(dictionary: dict[str, str]) -> dict[str, str]:
        return {value: key for key, value in dictionary.items()}

    data = pd.read_csv(filepath)
    data = data.reset_index()
    fistr_raw = data.loc[0].to_dict()
    reverse_fisrt_raw = get_reverse_dict(fistr_raw)

    for index, raw in data.iterrows():
        if index == 0:
            continue
        raw_dict = raw.to_dict()    
        raw_dict.pop('index')
        subscription = Subscription.objects.create(
            description=raw_dict[reverse_fisrt_raw['description']],
            image_cover="covers/" + str(raw_dict[reverse_fisrt_raw['image_cover']]),
            days_limit=raw_dict[reverse_fisrt_raw['days_limit']],
            price=raw_dict[reverse_fisrt_raw['price']],
            time_voice_limit=raw_dict[reverse_fisrt_raw['time_voice_limit']],
            title=raw_dict[reverse_fisrt_raw['title']],
            telegram_title=raw_dict[reverse_fisrt_raw['telegram_title']]
        )
        subscription.save()

    return 'Подписки созданы'


def voice_parser(filepath):
    VOICE = 'voice_name'
    CATEGORY = 'category'
    SUBCATEGORY = 'subcategory'
    SLUG_VOICE = 'slug_voice'
    SLUG_SUBCATEGORY = 'slug_subcategory'
    DESCRIPTION = 'description'
    GENDER = 'gender'
    SUBSCRIPTIOS = 'subscriptions'
    FILE = 'file_name'

    voice_counter = 0
    category_counter = 0
    subcategory_counter = 0

    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            media_data = MediaData.objects.create(
                slug=row[SLUG_VOICE],
                model_pth=os.environ.get('MEDIA_DATA_VOLUME').strip('/').split('/')[-1] + "/" + row[FILE] + ".pth",
                model_index=os.environ.get('MEDIA_DATA_VOLUME').strip('/').split('/')[-1] + "/" + row[FILE] + ".index",
                demka=os.environ.get('MEDIA_DATA_VOLUME').strip('/').split('/')[-1] + "/" + row[FILE] + ".mp3",
            )
            for sub in row[SUBSCRIPTIOS].split(', '):
                subscription = Subscription.objects.get(title=sub)

                category, category_created = Category.objects.get_or_create(
                    title=row[CATEGORY],
                    subscription=subscription
                )
                if category_created:
                    category_counter += 1
                    category.save()

                subcategory, subcategory_created = Subcategory.objects.get_or_create(
                    title=row[SUBCATEGORY],
                    category=category
                )
                if subcategory_created:
                    subcategory_counter += 1
                    subcategory.slug = row[SLUG_SUBCATEGORY]
                    subcategory.save()

                Voice.objects.create(
                    title=row[VOICE],
                    slug_voice=row[SLUG_VOICE],
                    description=row[DESCRIPTION],
                    gender=row[GENDER],
                    subcategory=subcategory,
                    media_data=media_data
                )
                voice_counter += 1

    return f'Голоса, категории и подкатегории созданы: {voice_counter} голосов, {category_counter} категорий, {subcategory_counter} подкатегорий'



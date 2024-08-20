import os
from django.db import transaction

import pandas as pd
import csv
from bot.models import Subscription, Category, Subcategory, Voice


@transaction.atomic
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
        raw_dict.pop("index")
        Subscription.objects.create(
            description=raw_dict[reverse_fisrt_raw["description"]],
            image_cover="data/" + str(raw_dict[reverse_fisrt_raw["image_cover"]]),
            days_limit=raw_dict[reverse_fisrt_raw["days_limit"]],
            price=raw_dict[reverse_fisrt_raw["price"]],
            time_voice_limit=raw_dict[reverse_fisrt_raw["time_voice_limit"]],
            title=raw_dict[reverse_fisrt_raw["title"]],
            telegram_title=raw_dict[reverse_fisrt_raw["telegram_title"]],
        )

    return "Подписки созданы"


@transaction.atomic
def voice_parser(filepath):
    VOICE = "voice_name"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    SLUG_VOICE = "slug_voice"
    SLUG_SUBCATEGORY = "slug_subcategory"
    DESCRIPTION = "description"
    GENDER = "gender"
    SUBSCRIPTIOS = "subscriptions"
    FILE = "file_name"
    SEARCH_WORDS = "search_alternatives"

    voice_counter = 0
    category_counter = 0
    subcategory_counter = 0

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row[CATEGORY]:
                category = None
            else:
                category, category_created = Category.objects.get_or_create(
                    title=row[CATEGORY],
                )
                if category_created:
                    category_counter += 1
                    category.save()

            if not row[SUBCATEGORY]:
                subcategory = None
            else:
                subcategory, subcategory_created = Subcategory.objects.get_or_create(
                    title=row[SUBCATEGORY], category=category
                )
                if subcategory_created:
                    subcategory_counter += 1
                    subcategory.slug = row[SLUG_SUBCATEGORY]
                    subcategory.save()

            voice = Voice.objects.create(
                title=row[VOICE],
                slug=row[SLUG_VOICE],
                description=row[DESCRIPTION],
                gender=row[GENDER],
                search_words=row[SEARCH_WORDS],
                subcategory=subcategory,
                model_pth=os.environ.get("MEDIA_DATA_VOLUME").strip("/").split("/")[-1] + "/" + row[FILE] + ".pth",
                model_index=os.environ.get("MEDIA_DATA_VOLUME").strip("/").split("/")[-1] + "/" + row[FILE] + ".index",
                demka=os.environ.get("MEDIA_DATA_VOLUME").strip("/").split("/")[-1] + "/" + row[FILE] + ".mp3",
                image=row[FILE] + ".png",
                demka_image=os.environ.get("MEDIA_DATA_VOLUME").strip("/").split("/")[-1] + "/" + row[FILE] + ".jpeg"
            )
            if row[SUBSCRIPTIOS]:
                for sub in row[SUBSCRIPTIOS].split(", "):
                    subscription = Subscription.objects.get(title=sub)
                    voice.subscriptions.add(subscription)

            voice_counter += 1

    return f"Голоса, категории и подкатегории созданы: {voice_counter} голосов, {category_counter} категорий, {subcategory_counter} подкатегорий"

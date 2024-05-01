import pandas as pd
import csv
from bot.models import Subscription


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
            image_cover=raw_dict[reverse_fisrt_raw['image_cover']],
            days_limit=raw_dict[reverse_fisrt_raw['days_limit']],
            price=raw_dict[reverse_fisrt_raw['price']],
            time_voice_limit=raw_dict[reverse_fisrt_raw['time_voice_limit']],
            title=raw_dict[reverse_fisrt_raw['title']]
        )
        subscription.save()

    return 'Подписки сохранены'


def voice_parser(filepath):
    VOICE = 'voice_name'
    CATEGORY = 'category'
    SUBCATEGORY = 'subcategory'
    SLUG = 'slug'
    DESCRIPTION = 'description'
    GENDER = 'gender'
    SUBSCRIPTION_TYPE = 'subscription_type_name'
    FILE = 'file_name'

    with open('arbuzikaibot_voices.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(
                row[VOICE],
                row[CATEGORY],
                row[SUBCATEGORY],
                row[SLUG],
                row[DESCRIPTION],
                row[GENDER],
                row[SUBSCRIPTION_TYPE],
                row[FILE]
            )

            # voice_name, category, subcategory, slug, description, gender, subscription_type_name, search, file_name

    return 'Подписки сохранены'



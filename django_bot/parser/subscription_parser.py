import os

import pandas as pd
from django.db import models


def read_file(filepath:str) -> pd.DataFrame:
    data = pd.read_csv(filepath)
    data = data.reset_index()
    return data


def get_reverse_dict(dictionary:dict[str, str]) -> dict[str, str]:
    return {value: key for key, value in dictionary.items()}


def write_to_subscription(model:models.Model, raw_dict:dict, title_dict:dict) -> None:
    subscription = model.objects.create(
            image_cover=raw_dict[title_dict['image_cover']], 
            days_limit=raw_dict[title_dict['days_limit']],
            price=raw_dict[title_dict['price']],
            time_voice_limit=raw_dict[title_dict['time_voice_limit']],
            title=raw_dict[title_dict['title']]
        )
    subscription.save()

# IT 's must be deprecated. The target is use the parser in adminka


def parser(apps, schema_editor):
    filepath = "parser/" + os.environ.get("SPREADSHEET")
    data = read_file(filepath)
    fistr_raw = data.loc[0].to_dict()
    reverse_fisrt_raw = get_reverse_dict(fistr_raw)
    Subcription = apps.get_model("bot", "Subscription")
    
    for index, raw in data.iterrows():
        if index == 0:
            continue
        raw_dict = raw.to_dict()    
        raw_dict.pop('index')
        write_to_subscription(Subcription, raw_dict, reverse_fisrt_raw)



from django.db import migrations
# from twison_to_db import parser

from ..django_bot.bot.models import Subscription


class Migration(migrations.Migration):
    dependencies = [
        ("Subscription", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(parser),
    ]
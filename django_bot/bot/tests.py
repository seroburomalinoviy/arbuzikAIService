from django.test import TestCase
from .models import User, Subscription, Category, CharacterModel

from uuid import uuid4
from datetime import datetime


class TestCreateInstances(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            category_name='/russians',
            category_index='1'
        )
        cls.char_model = CharacterModel.objects.create(
            model_index='1',
            file_path='/model.pth'
        )
        cls.subscription = Subscription.objects.create(
            name='Demo',
            time_voice_limit='30',
            price=100.0,
            days_limit=30,
            character_model_id=1,
            category_id=1
        )
        cls.user = User.objects.create(
            telegram_id=str(uuid4()),
            user_name='test_user',
            subscription_status='active',
            subscription_final_date=datetime.today(),
            subscription_usage_limit=10,
            tune='1 0 1 1 -2',
            subscription_id=1
        )

    def test_is_created(self):
        user_count = User.objects.count()
        self.assertEquals(user_count, 1)
        sub_count = Subscription.objects.count()
        self.assertEquals(sub_count, 1)
        char_model_count = CharacterModel.objects.count()
        self.assertEquals(char_model_count, 1)
        category_count = Category.objects.count()
        self.assertEquals(category_count, 1)



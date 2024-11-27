import json
import os
from telegram import Bot
from pydantic import BaseModel, Field


class RVCData:
    def __init__(self, arg):
        data = json.loads(arg)
        self.voice_model_index = data['voice_model_index']
        self.voice_model_pth = data['voice_model_pth']
        self.pitch = data['pitch']
        self.extension = data['extension']
        self.voice_name = data['voice_name']
        self.chat_id = data['chat_id']
        self.user_id = data['user_id']
        self.voice_title = data['voice_title']
        self.duration = data['duration']
        self.voice_filename = data['voice_filename']
        self.message_id = data['message_id']
        self.image = data.get("image")
        self.bot = Bot(token=os.environ.get("BOT_TOKEN"))


class Payment(BaseModel):
    order_id: int
    amount: int
    currency: str
    merchant_id: int
    order_id: int
    status: bool
    service: str
    bot = Bot(token=os.environ.get("BOT_TOKEN"))

# class Payment:
#     def __init__(self, arg):
#         data = json.loads(arg)
#         self.order_id = data['order_id']
#         self.amount = data['amount']
#         self.currency = data['currency']
#         self.merchant_id = data['merchant_id']
#         self.order_id = data['order_id']
#         self.status = data['status']
#         self.service = data['service']
#         self.bot = Bot(token=os.environ.get("BOT_TOKEN"))


class PayUrl:
    def __init__(self, arg):
        data = json.loads(arg)
        self.type = data['type']
        self.url = data['url']
        self.subscription_title = data['subscription_title']
        self.order_id = data['order_id']
        self.amount = data['amount']
        self.chat_id = data['chat_id']
        self.bot = Bot(token=os.environ.get("BOT_TOKEN"))

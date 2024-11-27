import json
import os
from telegram import Bot
from pydantic import BaseModel
from typing import ClassVar


class RVCData(BaseModel):
    voice_model_index: str = ''
    voice_model_pth: str = ''
    pitch: str = ''
    extension: str = ''
    voice_name: str = ''
    voice_filename: str = ''
    chat_id: str = ''
    user_id: str = ''
    voice_title: str = ''
    duration: int
    message_id: int
    bot: ClassVar = Bot(token=os.environ.get("BOT_TOKEN"))


class Payment(BaseModel):
    order_id: int
    amount: int
    currency: str
    merchant_id: int
    order_id: int
    status: bool
    service: str
    bot: ClassVar = Bot(token=os.environ.get("BOT_TOKEN"))


class PayUrl(BaseModel):
    type: str = ''
    url: str = ''
    subscription_title: str = ''
    order_id: int
    amount: int
    chat_id: str = ''
    bot: ClassVar = Bot(token=os.environ.get("BOT_TOKEN"))


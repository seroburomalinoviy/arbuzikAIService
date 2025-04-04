from os import getenv
from telegram import Bot
from pydantic import BaseModel
from typing import ClassVar


class RVCData(BaseModel):
    voice_model_index: str = ''
    voice_model_pth: str = ''
    pitch: int
    extension: str = ''
    voice_name: str = ''
    voice_filename: str = ''
    chat_id: str = ''
    user_id: str = ''
    voice_title: str = ''
    duration: float
    message_id: int
    bot: ClassVar = Bot(token=getenv("BOT_TOKEN"))


class Payment(BaseModel):
    status: str
    merchant_id: str = ''
    invoice_id: str = ''
    order_id: str
    amount: str
    currency: str
    sign: str = ''
    service: str = ''
    bot: ClassVar = Bot(token=getenv("BOT_TOKEN"))


class PayUrl(BaseModel):
    payment_id: str = ''
    type: str = ''
    url: str = ''
    subscription_title: str
    order_id: str
    amount: int
    chat_id: int
    service: str
    bot: ClassVar = Bot(token=getenv("BOT_TOKEN"))

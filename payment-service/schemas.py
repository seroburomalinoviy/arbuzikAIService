import json
from pydantic import BaseModel
from typing import ClassVar


class PayUrl(BaseModel):
    payment_id: str = ''
    type: str
    url: str
    subscription_title: str
    order_id: str
    amount: int
    chat_id: int
    service: str


class Payment(BaseModel):
    status: str
    merchant_id: str
    invoice_id: str
    order_id: str
    amount: str
    currency: str
    sign: str




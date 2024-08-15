import json

from pydantic import BaseModel
import uuid


class Order:
    def __init__(self, arg: str):
        data = json.loads(arg)
        self.subscription_title = data['subscription_title']
        self.order_id = data['order_id']
        self.amount = data['amount']
        self.chat_id = data['chat_id']


class Payment(BaseModel):
    status: str
    merchant_id: uuid
    invoice_id: uuid
    order_id: str
    amount: float
    currency: str
    sign: str


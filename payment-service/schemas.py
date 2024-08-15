import json

from pydantic import BaseModel
import uuid


class Order:
    def __init__(self, arg: str):
        data = json.loads(arg)
        self.subscription_title: str = data['subscription_title']
        self.order_id: str = data['order_id']
        self.amount: str = data['amount']
        self.chat_id: str = data['chat_id']


class ApiPayment(BaseModel):
    status: str
    merchant_id: str
    invoice_id: str
    order_id: str
    amount: str
    currency: str
    sign: str


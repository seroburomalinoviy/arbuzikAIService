import json
from pydantic import BaseModel
from typing import ClassVar


class PayUrl(BaseModel):
    type: str | None
    url: str | None
    subscription_title: str
    order_id: str
    amount: str
    chat_id: int


# class Order:
#     def __init__(self, arg: str):
#         data = json.loads(arg)
#         self.subscription_title: str = data['subscription_title']
#         self.order_id: str = data['order_id']
#         self.amount: str = data['amount']
#         self.chat_id: str = data['chat_id']


class ApiPayment:
    def __init__(self, data: json):
        self.status: str = data['status']
        self.merchant_id: str = data['merchant_id']
        self.invoice_id: str = data['invoice_id']
        self.order_id: str = data['order_id']
        self.amount: str = data['amount']
        self.currency: str = data['currency']
        self.sign: str = data['sign']



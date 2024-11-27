import json
from pydantic import BaseModel
from typing import ClassVar


class PayUrl(BaseModel):
    type: str
    url: str
    subscription_title: str
    order_id: str
    amount: int
    chat_id: int


class ApiPayment:
    def __init__(self, data: json):
        self.status: str = data['status']
        self.merchant_id: str = data['merchant_id']
        self.invoice_id: str = data['invoice_id']
        self.order_id: str = data['order_id']
        self.amount: str = data['amount']
        self.currency: str = data['currency']
        self.sign: str = data['sign']



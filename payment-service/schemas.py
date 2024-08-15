import json
from typing import Annotated

from pydantic import BaseModel
from fastapi import Form


class Order:
    def __init__(self, arg: str):
        data = json.loads(arg)
        self.subscription_title: str = data['subscription_title']
        self.order_id: str = data['order_id']
        self.amount: str = data['amount']
        self.chat_id: str = data['chat_id']


class ApiPayment(BaseModel):
    status: Annotated[str, Form()]
    merchant_id: Annotated[str, Form()]
    invoice_id: Annotated[str, Form()]
    order_id: Annotated[str, Form()]
    amount: Annotated[str, Form()]
    currency: Annotated[str, Form()]
    sign: Annotated[str, Form()]


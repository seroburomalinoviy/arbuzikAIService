import httpx
import hashlib
import uuid
from urllib.parse import urlencode
import logging
from dotenv import load_dotenv
import os
import json

from schemas import Order

load_dotenv()
logger = logging.getLogger(__name__)


async def create_hash(key: str):
    sign = hashlib.sha256()
    sign.update(key.encode())
    return sign.hexdigest()


async def get_payment_url(data: str) -> dict:
    order = Order(data)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "merchant_id": uuid.UUID(os.environ.get("MERCHANT_ID")),
        "amount": order.amount,
        "order_id": order.order_id,
        "currency": "RUB",
        "desc": order.subscription_title,
        "lang": "ru",
    }

    secret_key_1 = os.environ.get("SECRET_KEY_1")
    key = f'{str(data["merchant_id"])}:{data["amount"]}:{data["currency"]}:{secret_key_1}:{data["order_id"]}'
    body["sign"] = await create_hash(key)

    client = httpx.AsyncClient()
    try:
        response = await client.post(
            "https://aaio.so/merchant/get_pay_url",
            data=urlencode(body),
            headers=headers,
        )
    except Exception as e:
        logger.error(f'Error during request to  aaio {e}')

    await client.aclose()

    if response.status_code != 200:
        logger.warning(f'Error during request to  aaio status_code: {response.status_code}')

    return response.json() | data


async def get_actual_ips() -> list:
    client = httpx.AsyncClient()

    try:
        response = await client.get('https://aaio.so/api/public/ips')
    except Exception as e:
        logger.error(e)

    if response.status_code != 200:
        logger.warning(f'Error during request to  aaio status_code: {response.status_code}')

    await client.aclose()

    return response.json().get('list')

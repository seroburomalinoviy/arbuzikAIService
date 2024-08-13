import httpx
import hashlib
import uuid
from urllib.parse import urlencode
import logging
from dotenv import load_dotenv
import os
import json

load_dotenv()
logger = logging.getLogger(__name__)


async def create_hash(data: dict):
    secret_key_1 = os.environ.get("SECRET_KEY_1")
    sign = hashlib.sha256()
    key = f'{data["merchant_id"]}:{data["amount"]}:{data["currency"]}:{secret_key_1}:{data["order_id"]}'
    sign.update(key.encode())
    return sign.hexdigest()


async def get_payment_url(data: str) -> dict:
    data = json.loads(data)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "merchant_id": uuid.UUID(os.environ.get("MERCHANT_ID")),
        "amount": data.get("amount"),
        "order_id": data.get("order_id"),
        "currency": "RUB",
        "desc": data.get("subscription_title"),
        "lang": "ru",
    }
    body["sign"] = await create_hash(body)

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

    return response.json()


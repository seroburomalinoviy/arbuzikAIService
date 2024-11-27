import httpx
import hashlib
import uuid
from urllib.parse import urlencode
import logging
from dotenv import load_dotenv
import os
import json

from schemas import PayUrl

load_dotenv()

AAIO_CREATE_ORDER = os.environ.get("AAIO_CREATE_ORDER")
AAIO_IPS = os.environ.get("AAIO_IPS")


async def create_hash(key: str):
    sign = hashlib.sha256()
    sign.update(key.encode())
    return sign.hexdigest()


async def get_payment_url(data: str) -> dict:
    """
    Создание заказа

    :param data:
    :return:
    """
    order = PayUrl(**json.loads(data))
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    merchant_id = uuid.UUID(os.environ.get("MERCHANT_ID"))
    currency = "RUB"

    body = {
        "merchant_id": merchant_id,
        "amount": order.amount,
        "order_id": order.order_id,
        "currency": currency,
        "desc": order.subscription_title,
        "lang": "ru"
    }

    secret_key_1 = os.environ.get("SECRET_KEY_1")
    key = f'{str(merchant_id)}:{order.amount}:{currency}:{secret_key_1}:{order.order_id}'
    body["sign"] = await create_hash(key)

    logging.info(f"Create order in aaio: url={AAIO_CREATE_ORDER}, {body=}")
    client = httpx.AsyncClient()
    try:
        response = await client.post(
            url=AAIO_CREATE_ORDER,
            data=urlencode(body),
            headers=headers,
        )
    except Exception as e:
        logging.error(f'Error during request to  aaio {e}')

    await client.aclose()

    if response.status_code != 200:
        logging.warning(f'Error during request to  aaio status_code: {response.status_code}')

    logging.info(f"{response=}")

    ans = response.json()

    logging.info(f"{ans=}")

    order.type = ans.get("type")
    order.url = ans.get("url")

    logging.info(f"created order data: {order.model_dump()}")

    return order.model_dump()


async def get_actual_ips() -> list:
    client = httpx.AsyncClient()

    try:
        response = await client.get(url=AAIO_IPS)
    except Exception as e:
        logging.error(e)
        raise Exception('cant get actual ips')

    if response.status_code != 200:
        logging.warning(f'Error during request to  aaio status_code: {response.status_code}')

    await client.aclose()

    return response.json().get('list')

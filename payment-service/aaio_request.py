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


async def create_hash(key: str):
    sign = hashlib.sha256()
    sign.update(key.encode())
    return sign.hexdigest()


async def get_payment_url(data: str):
    order = PayUrl(**json.loads(data))
    if order.service == 'aaio':
        return await get_aaio_url(order)
    elif order.service == 'ukassa':
        return await get_ukassa_url(order)
    else:
        return None


async def get_ukassa_url(order: PayUrl) -> json:
    UKASSA_API_URL = os.getenv("UKASSA_API_URL")
    UKASSA_SHOP_ID = os.getenv("UKASSA_SHOP_ID")
    UKASSA_SECRET_KEY = os.getenv("UKASSA_SECRET_KEY")
    UKASSA_CUSTOMER_EMAIL = os.getenv("UKASSA_CUSTOMER_EMAIL")
    UKASSA_REDIRECT_URL = os.getenv("UKASSA_REDIRECT_URL")

    currency = "RUB"
    header = {
        "Idempotence-Key": str(uuid.uuid4()).encode(),
        "Content-Type": "application/json"
    }
    data = {
        "amount": {
          "value": str(order.amount),
          "currency": currency
        },
        "receipt": {
            "customer": {
                "email": UKASSA_CUSTOMER_EMAIL
            },
            "items": [
                {
                    "description": order.subscription_title,
                    "quantity": 1,
                    "vat_code": 1,
                    "amount": {
                        "value": str(order.amount),
                        "currency": currency
                    }
                }
            ]
        },
        "capture": True,
        "confirmation": {
          "type": "redirect",
          "return_url": UKASSA_REDIRECT_URL
        },
        "description": order.subscription_title
      }

    auth = httpx.BasicAuth(username=UKASSA_SHOP_ID, password=UKASSA_SECRET_KEY)
    client = httpx.AsyncClient(auth=auth)
    try:
        response = await client.post(
            url=UKASSA_API_URL,
            headers=header,
            json=data
        )
    except Exception as e:
        logging.error(f"Ukassa request error: {e}")
    else:
        await client.aclose()

    if response.status_code != 200:
        msg = f'Error during request to  ukassa status_code: {response.status_code}\n{response.json()=}'
        logging.warning(msg)

    ans = response.json()
    order.url = ans['confirmation']['confirmation_url']
    order.type = ans.get('status')
    order.payment_id = ans.get('id')

    logging.info(f"created order data: {order.model_dump()}")

    return order.model_dump()


async def get_aaio_url(order: PayUrl) -> json:
    """
    Создание заказа

    :param order:
    :return order:
    """
    AAIO_CREATE_ORDER = os.environ.get("AAIO_CREATE_ORDER")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    AAIO_MERCHANT_ID = uuid.UUID(os.environ.get("AAIO_MERCHANT_ID"))
    currency = "RUB"

    body = {
        "merchant_id": AAIO_MERCHANT_ID,
        "amount": order.amount,
        "order_id": order.order_id,
        "currency": currency,
        "desc": order.subscription_title,
        "lang": "ru"
    }

    secret_key_1 = os.environ.get("AAIO_SECRET_KEY_1")
    key = f'{str(AAIO_MERCHANT_ID)}:{order.amount}:{currency}:{secret_key_1}:{order.order_id}'
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

    ans = response.json()
    order.type = ans.get("type")
    order.url = ans.get("url")

    logging.info(f"created order data: {order.model_dump()}")

    return order.model_dump()


async def get_actual_ips() -> list:
    AAIO_IPS = os.environ.get("AAIO_IPS")
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

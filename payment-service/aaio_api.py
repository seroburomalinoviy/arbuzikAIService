import httpx
import asyncio
import hashlib
import uuid
from urllib.parse import urlencode

secret_key_1 = "02d6bb4e05d6475740f74d8677c1554f"


async def create_hash(data):
    sign = hashlib.sha256()
    key = f'{data["merchant_id"]}:{data["amount"]}:{data["currency"]}:{secret_key_1}:{data["order_id"]}'
    sign.update(key.encode())
    return sign.hexdigest()


async def make_payment():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "merchant_id": uuid.UUID("202a19e7-bc3d-4746-899c-d1787c300a56"),
        "amount": 10,
        "order_id": "order-test",
        "currency": "RUB",
        "desc": "Название подписки",
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
        print(f"Some errors: {e}")

    print(response.text)

    await client.aclose()


if __name__ == "__main__":
    asyncio.run(make_payment())

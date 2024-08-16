from ampq_driver import push_amqp_message
from aaio_request import get_actual_ips, create_hash

import os
import logging
from schemas import ApiPayment
from fastapi import FastAPI, Request, Header
from fastapi.responses import Response, HTMLResponse
from fastapi.encoders import jsonable_encoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI(redoc_url=None)


@app.get('/check')
async def check(request: Request, remote_ip: str = Header(None, alias='X-Real-IP')):
    return HTMLResponse(content=f"Success: your ip: {remote_ip}", status_code=200)


@app.post('/payment')
async def get_payment(request: Request) -> Response:
    f = await request.form()
    json_f = jsonable_encoder(f)
    payment = ApiPayment(json_f)

    logger.info(f'{json_f=}')

    ip_request: str = request.client.host
    logger.info(f'{ip_request=}')
    ips_allowed: list = await get_actual_ips()
    logger.info(f'{ips_allowed=}')

    if ip_request not in ips_allowed:
        logger.warning('Not allowed ip!')
        # return Response(status_code=400)

    secret_key_2 = os.environ.get('SECRET_KEY_2')
    key = f'{payment.merchant_id}:{payment.amount}:{payment.currency}:{secret_key_2}:{payment.order_id}'
    internal_sign = await create_hash(key)

    if internal_sign != payment.sign:
        logger.warning('No appropriated sign!')
        # return Response(status_code=400)

    data = {
        'order_id': payment.order_id,
        'amount': payment.amount,
        'currency': payment.currency,
        'merchant_id': payment.merchant_id,
        'status': True
    }

    await push_amqp_message(data, routing_key='payment-to-bot')
    return Response(status_code=200)

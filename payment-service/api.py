import json

from amqp.driver import push_amqp_message
from amqp.aaio_request import get_actual_ips, create_hash

import os
import logging
from logging.config import dictConfig
import logging_config
from amqp.schemas import Payment
from fastapi import FastAPI, Request, Header
from fastapi.responses import Response, HTMLResponse
from fastapi.encoders import jsonable_encoder

os.makedirs('/logs', exist_ok=True)

logging.getLogger('uvicorn').setLevel(logging.WARNING)
dictConfig(logging_config.config)
logger = logging.getLogger(__name__)
app = FastAPI(redoc_url=None)


@app.get('/check')
async def check():
    return HTMLResponse(content="<h1><b><i><u>Success</u></i></b></h1>", status_code=200)


@app.post('/payment')
async def get_payment(request: Request, remote_ip: str = Header(None, alias='X-Real-IP')) -> Response:
    f = await request.form()
    json_f = await jsonable_encoder(f)
    payment = Payment(**json.loads(json_f))

    logger.info(f'{json_f=}')

    ips_allowed: list = await get_actual_ips()
    logger.info(f'{ips_allowed=}, {remote_ip=}')

    if remote_ip not in ips_allowed:
        logger.warning('Not allowed ip!')
        return Response(status_code=400)

    secret_key_2 = os.environ.get('AAIO_SECRET_KEY_2')
    key = f'{payment.merchant_id}:{payment.amount}:{payment.currency}:{secret_key_2}:{payment.order_id}'
    internal_sign = await create_hash(key)

    if internal_sign != payment.sign:
        logger.warning('No appropriated sign!')
        return Response(status_code=400)

    await push_amqp_message(payment.model_dump(), routing_key='payment-to-bot')
    return Response(status_code=200)

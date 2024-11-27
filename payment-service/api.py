import json

from ampq_driver import push_amqp_message
from aaio_request import get_actual_ips, create_hash

import os
import logging
from logging.handlers import RotatingFileHandler
from schemas import ApiPayment
from fastapi import FastAPI, Request, Header
from fastapi.responses import Response, HTMLResponse
from fastapi.encoders import jsonable_encoder

os.makedirs('/logs', exist_ok=True)
rotating_handler = RotatingFileHandler('/logs/payment-api.log', backupCount=5, maxBytes=512 * 1024)
log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
formatter = logging.Formatter(log_format)
rotating_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
logging.getLogger('uvicorn.error').addHandler(rotating_handler)

app = FastAPI(redoc_url=None)


@app.get('/check')
async def check():
    return HTMLResponse(content="<h1><b><i><u>Success</u></i></b></h1>", status_code=200)


@app.post('/payment')
async def get_payment(request: Request, remote_ip: str = Header(None, alias='X-Real-IP')) -> Response:
    f = await request.form()
    json_f = await jsonable_encoder(f)
    payment = ApiPayment(**json.loads(json_f))

    logging.info(f'{json_f=}')

    ips_allowed: list = await get_actual_ips()
    logging.info(f'{ips_allowed=}, {remote_ip=}')

    if remote_ip not in ips_allowed:
        logging.warning('Not allowed ip!')
        return Response(status_code=400)

    secret_key_2 = os.environ.get('SECRET_KEY_2')
    key = f'{payment.merchant_id}:{payment.amount}:{payment.currency}:{secret_key_2}:{payment.order_id}'
    internal_sign = await create_hash(key)

    if internal_sign != payment.sign:
        logging.warning('No appropriated sign!')
        return Response(status_code=400)

    await push_amqp_message(payment.model_dump(), routing_key='payment-to-bot')
    return Response(status_code=200)

from ampq_driver import push_amqp_message

from typing import Union
from fastapi import FastAPI, responses

app = FastAPI(redoc_url=None)


@app.get('/payment/success')
async def get_payment(order_id: Union[str, None] = None, amount: Union[str, None] = None, currency: Union[str, None] = None):
    await push_amqp_message({'order_id': order_id, 'amount': amount, 'currency': currency, 'success': True},
                            routing_key='payment-to-bot')
    return responses.Response(status_code=200)


@app.get('/payment/failure')
async def get_payment(order_id: Union[str, None] = None, amount: Union[str, None] = None, currency: Union[str, None] = None):
    await push_amqp_message({'order_id': order_id, 'amount': amount, 'currency': currency, 'success': False},
                            routing_key='payment-to-bot')
    return responses.Response(status_code=200)

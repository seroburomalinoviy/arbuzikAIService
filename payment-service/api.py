from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get('/payment/success')
async def get_payment(order_id: Union[str, None] = None, amount: Union[str, None] = None, currency: Union[str, None] = None):
    return {'order_id': order_id, 'amount': amount}


@app.get('/payment/failure')
async def get_payment(order_id: Union[str, None] = None, amount: Union[str, None] = None, currency: Union[str, None] = None):
    return {'order_id': order_id, 'amount': amount}


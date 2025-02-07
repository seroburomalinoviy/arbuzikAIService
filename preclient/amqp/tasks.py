import httpx
import redis
import os
import logging


async def create_task(payload: str):

    r = redis.StrictRedis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        db=0,
        retry_on_timeout=True
    )
    async with httpx.AsyncClient() as client:
        response = await client.get('http://prometheus-server:9001/api/add_task')
    logging.info(f"Response from prometheus-server: {response.status_code}")

    name_of_list = "raw-data"
    resp = r.lpush(name_of_list, payload)
    logging.info(resp)

import httpx
import redis
import os
import logging
from dotenv import load_dotenv

load_dotenv()


async def create_task(payload: str):
    host, port = os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT')
    try:
        r = redis.StrictRedis(host=host, port=int(port), db=0, retry_on_timeout=True)
    except redis.exceptions.ConnectionError:
        logging.info(f"Redis ConnectionError: {host=} {port=}")
    except Exception as e:
        logging.info(f"Exception during Redis connection\n{e}")
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get('http://prometheus-server:9001/api/add_task')
        logging.info(f"Response from prometheus-server: {response.status_code}")

        name_of_list = "raw-data"
        resp = r.lpush(name_of_list, payload)
        logging.info(resp)

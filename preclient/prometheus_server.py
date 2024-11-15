from fastapi import FastAPI, status
from prometheus_client import Gauge, make_asgi_app
from pydantic import BaseModel
import logging
from fastapi.logger import logger

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
logger.setLevel(level=gunicorn_logger.level)

# log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
# logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
#
# logger = logging.getLogger(__name__)


# class SpeedModel(BaseModel):
#     speed: float


TASKS = Gauge('tasks', 'Created tasks of the ArbuzikAiBot')
COMPLETE_TASKS = Gauge('complete_tasks', 'Completed tasks of the ArbuzikAiBot')
SPEED = Gauge('speed', 'Time of 1 task processing')

app = FastAPI(debug=True, redoc_url=None)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get('/api/add_task')
async def add_task():
    TASKS.inc()
    return status.HTTP_200_OK


@app.get('/api/complete_task')
async def complete_task():
    COMPLETE_TASKS.inc()
    return status.HTTP_200_OK


@app.post('/api/add_speed')
async def add_speed(data):
    print(data)
    logger.info(f"{data=}")
    SPEED.set(data.get("speed"))
    return data

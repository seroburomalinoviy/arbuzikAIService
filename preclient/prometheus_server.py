from fastapi import FastAPI, status
from prometheus_client import Gauge, make_asgi_app, Histogram
import logging

logger = logging.getLogger('uvicorn.error')


TASKS = Gauge('tasks', 'Created tasks of the ArbuzikAiBot')
COMPLETE_TASKS = Gauge('complete_tasks', 'Completed tasks of the ArbuzikAiBot')
SPEED = Gauge('speed', 'Speed of 1 task processing')

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


@app.post('/api/add_speed/')
async def add_speed(data: dict[str, float]):
    logger.info(f"{data=}")
    SPEED.set(data.get("speed"))
    SPEED.set(0)
    return status.HTTP_200_OK

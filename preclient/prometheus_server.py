from fastapi import FastAPI, status
from prometheus_client import Gauge, make_asgi_app

RAW_TASKS = Gauge('raw_tasks', 'Description of gauge')

app = FastAPI(debug=False, redoc_url=None)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get('/api/add_task')
def add_task():
    RAW_TASKS.inc()
    return status.HTTP_200_OK


@app.get('/api/complete_task')
def add_task():
    RAW_TASKS.dec()
    return status.HTTP_200_OK

from fastapi import FastAPI, status
from prometheus_client import Gauge, make_asgi_app

TASKS = Gauge('tasks', 'Created tasks of the ArbuzikAiBot')
COMPLETE_TASKS = Gauge('complete_tasks', 'Completed tasks of the ArbuzikAiBot')

app = FastAPI(debug=False, redoc_url=None)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get('/api/add_task')
def add_task():
    TASKS.inc()
    return status.HTTP_200_OK


@app.get('/api/complete_task')
def complete_task():
    COMPLETE_TASKS.inc()
    return status.HTTP_200_OK

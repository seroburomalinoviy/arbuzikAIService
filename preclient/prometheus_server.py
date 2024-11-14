from fastapi import FastAPI
from prometheus_client import make_asgi_app

# REQUEST_COUNT = Counter('app_requests_total', 'Total request count')
# CURRENT_REQUESTS = Gauge('app_requests_inprogress', 'Requests currently in progress')

# app = FastAPI(debug=False)
# # Add prometheus asgi middleware to route /metrics requests


from fastapi import FastAPI, status
from prometheus_client import generate_latest, Gauge

RAW_TASKS = Gauge('raw_tasks', 'Description of gauge')

app = FastAPI(debug=False, redoc_url=None)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get('/api/new_raw_task')
@RAW_TASKS.time()
def new_raw_task():
    RAW_TASKS.inc()
    return status.HTTP_200_OK

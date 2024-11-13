from fastapi import FastAPI
from prometheus_client import Gauge

app = FastAPI(redoc_url=None)

# REQUEST_COUNT = Counter('app_requests_total', 'Total request count')
# CURRENT_REQUESTS = Gauge('app_requests_inprogress', 'Requests currently in progress')
RAW_TASKS = Gauge('raw_tasks', 'Description of gauge')


@app.get('/metrics')
def hello():
    return RAW_TASKS


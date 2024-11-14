from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI(debug=False)

# REQUEST_COUNT = Counter('app_requests_total', 'Total request count')
# CURRENT_REQUESTS = Gauge('app_requests_inprogress', 'Requests currently in progress')


# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


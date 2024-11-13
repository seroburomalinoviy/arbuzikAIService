from prometheus_client import start_wsgi_server
import os
from dotenv import load_dotenv
import logging
import asyncio


load_dotenv()


if __name__ == "__main__":
    # start_http_server(int(os.environ.get("PROMETHEUS_PORT")))
    start_wsgi_server(9090)
    logging.info(f"Prometheus server started")

    # app = make_asgi_app()

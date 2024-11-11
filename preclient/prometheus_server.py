from prometheus_client import start_http_server, make_asgi_app
import os
from dotenv import load_dotenv
import logging


load_dotenv()


if __name__ == "__main__":
    start_http_server("8010")
    # start_http_server(os.environ.get("PROMETHEUS_PORT"))
    logging.info(f"Prometheus server started")

    # app = make_asgi_app()

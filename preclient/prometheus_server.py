from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

import os
from dotenv import load_dotenv
import logging
import asyncio


load_dotenv()


if __name__ == "__main__":
    # start_http_server(int(os.environ.get("PROMETHEUS_PORT")))

    app = Flask(__name__)
    # Add prometheus wsgi middleware to route /metrics requests
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })
    logging.info(f"Prometheus server started")


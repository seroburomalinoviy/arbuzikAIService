from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server
import os
from dotenv import load_dotenv
import logging
import asyncio


load_dotenv()


if __name__ == "__main__":
    # start_http_server(int(os.environ.get("PROMETHEUS_PORT")))
    app = make_wsgi_app()
    httpd = make_server('', 9090, app)
    httpd.serve_forever()
    logging.info(f"Prometheus server started")

    # app = make_asgi_app()

from prometheus_client import make_asgi_app

import os
from dotenv import load_dotenv
import logging
import asyncio


load_dotenv()


if __name__ == "__main__":
    # start_http_server(int(os.environ.get("PROMETHEUS_PORT")))

    app = make_asgi_app(disable_compression=True)
    asyncio.run(app)
    logging.info(f"Prometheus server started")

    # app = make_asgi_app()

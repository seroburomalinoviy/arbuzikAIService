from prometheus_client import start_http_server
import os
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    start_http_server(os.environ.get("PROMETHEUS_PORT"))
import asyncio
import logging
import os

from ampq_driver import amqp_listener


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    rotating_handler = logging.handlers.RotatingFileHandler('/logs/payment-listener.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    rotating_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('').addHandler(rotating_handler)

    asyncio.run(amqp_listener())


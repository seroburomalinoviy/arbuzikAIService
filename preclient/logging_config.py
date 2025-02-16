config = {
    "version": 1,
    "formatters": {
        "main": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "main",
            "filename": "/logs/bot.log",
            "backupCount": 5,
            "maxBytes": 512 * 1024,
        },
        "stream": {
            "class": "logging.StreamHandler",
            "formatter": "main",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "stream_json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "level": "INFO",
            "handlers": ["file", "stream_json"],
            "propagate": False
        },
        "__main__": {
            "level": "INFO",
        },
        "prometheus_server": {
            "level": "INFO",
        },
        "amqp.driver": {
            "level": "INFO",
        },
        "amqp.tasks": {
            "level": "INFO",
        }
    }
}

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
        "json_journal": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s - %(message)s"
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
        "stream_journal": {
            "class": "logging.StreamHandler",
            "formatter": "json_journal",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
    },
    "loggers": {
        "": {  # root logger
            "level": "INFO",
            "handlers": ["file", "stream"],
            "propagate": False
        },
        "__main__": {
            "level": "INFO",
        },
        "bot.tasks": {
            "level": "INFO",
        },
        "bot.config.celery": {
            "level": "INFO",
        },
        "bot.handler.main": {
            "level": "INFO",
        },
        "bot.logic.utils": {
            "level": "INFO",
            "handlers": ["file", "stream_journal"],
            "propagate": False
        },
        "bot.logic.setup": {
            "level": "INFO",
        },
        "bot.logic.amqp.driver": {
            "level": "INFO",
        },
        "bot.logic.amqp.tasks": {
            "level": "INFO",
        },
        "bot.handlers.search": {
            "level": "INFO",
        }
    }
}

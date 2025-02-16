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
        "utils": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s - JOURNAL - %(name)s - %(message)s"
        },
    },
    "handlers": {
        "utils_json_console": {
            "class": "logging.StreamHandler",
            "formatter": "utils",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/logs/bot.log",
            "backupCount": 5,
            "maxBytes": 512 * 1024,
            "formatter": "main"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "main",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "": {  # root logger
            "level": "INFO",
            "handlers": ["file", "json"],
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
            "handlers": ["file", "utils_json_console"],
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

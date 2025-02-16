config = {
    "version": 1,
    "formatters": {
        "main": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
        },
        "json_formatter": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
        }
    },
    "handlers": {
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
        "json_handler": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "": {  # root logger
            "level": "INFO",
            "handlers": ["file", "json_handler"],
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

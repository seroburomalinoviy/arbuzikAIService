config = {
    "version": 1,
    "formatters": {
        "main": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/logs/preclient.log",
            "backupCount": 5,
            "maxBytes": 512 * 1024,
            "formatter": "main"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "main",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "": {  # root logger
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False
        },
        "__main__": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False
        }
    }
}

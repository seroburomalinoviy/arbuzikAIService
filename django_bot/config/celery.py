import os
import logging
from logging.handlers import RotatingFileHandler
from celery import Celery
from celery.signals import after_setup_logger
from celery.schedules import crontab

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# redis_for_celery = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/1"
redis_for_celery = f"redis://redis:{os.environ.get('REDIS_PORT')}/1"

app = Celery("django_bot", broker=redis_for_celery)
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    worker_hijack_root_logger=False,
    broker_connection_retry_on_startup=True,
    broker_transport_options={'visibility_timeout': 21600},
    result_backend_transport_options={'visibility_timeout': 21600},
    visibility_timeout=21600,
)

app.autodiscover_tasks()


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    handler = RotatingFileHandler('/logs/celery-worker.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logger.addHandler(handler)


app.conf.beat_schedule = {
    'clean_user_voices': {
        'task': 'bot.logic.celery_tasks.clean_user_voices',  # path to task
        'schedule': crontab(minute='0', hour='3'),  # How often the task should run
        # 'schedule': 60.0,  # каждую минуту
        # 'args': (arg1, arg2),  # Positional arguments for the task (optional)
        # 'kwargs': {'keyword_arg': 'value'},  # Keyword arguments for the task (optional)
    },
    # Add more tasks as needed
}



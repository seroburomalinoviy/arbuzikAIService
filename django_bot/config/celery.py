import os
import logging
from logging.handlers import RotatingFileHandler
from celery import Celery
from celery.signals import after_setup_logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
redis_for_celery = f"redis://:{os.environ.get('REDIS_PASSWORD')}@{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/1"

app = Celery("django_bot", broker=redis_for_celery)
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    worker_hijack_root_logger=False,
)
app.autodiscover_tasks()


@after_setup_logger.connect
def setup_loggers(*args, **kwargs):
    os.makedirs('/logs', exist_ok=True)
    handler = RotatingFileHandler('/logs/celery.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('').addHandler(handler)


@app.task
def clean_user_voices():
    print('User voices was cleaned up')
    logging.info('User voices was cleaned up')
    os.remove(f'{os.environ.get("USER_VOICES")}/*')


app.conf.beat_schedule = {
    'clean_user_voices': {
        'task': 'bot.tasks.clean_user_voices',  # The name of the task
        # 'schedule': crontab(minute='0', hour='3'),  # How often the task should run
        'schedule': 60.0,  # каждую минуту
        # 'args': (arg1, arg2),  # Positional arguments for the task (optional)
        # 'kwargs': {'keyword_arg': 'value'},  # Keyword arguments for the task (optional)
    },
    # Add more tasks as needed
    'debug_task': {
        'task': 'config.celery.debug_task',
        'schedule': 60.0
    }
}


# Celery settings
#
# CELERY_BROKER_URL = redis_for_celery
# CELERY_RESULT_BACKEND = redis_for_celery
# CELERY_CACHE_BACKEND = redis_for_celery
# CELERY_ACCEPT_CONTENT = ["application/json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
# CELERY_TIMEZONE = TIME_ZONE
#
# # Celery Beat settings
# CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"




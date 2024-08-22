from config.celery import celery_app
import os
import logging


@celery_app.task()
def clean_user_voices():
    # logging.info('START TASK')
    print('hauhai')
    os.remove(f'{os.environ.get("USER_VOICES")}/*')
    # logging.info('User voices was cleaned up')



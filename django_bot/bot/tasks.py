from celery import shared_task
import os
import logging


@shared_task
def clean_user_voices():
    os.system(f'rm -rf {os.environ.get("USER_VOICES")}/')
    logging.info('User voices was cleaned up')



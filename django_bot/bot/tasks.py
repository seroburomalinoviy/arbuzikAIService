from config.celery import app
import os
import logging


@app.task
def clean_user_voices():
    # logging.info('START TASK')
    print('hauhai')
    os.remove(f'{os.environ.get("USER_VOICES")}/*')
    return True
    # logging.info('User voices was cleaned up')



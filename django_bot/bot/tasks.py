import os
import logging
import django
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout
import json
import amqp
from dotenv import load_dotenv
import os

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from config.celery import app
from user.models import Order

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def clean_user_voices():
    os.system(f'rm -rf {os.environ.get("USER_VOICES")}/*')
    logger.info('User voices was cleaned up')
    return True


@app.task(ignore_result=False)
def check_payment_api(order_id: str):
    AAIO_INFO = os.environ.get("AAIO_INFO")
    AAIO_API_KEY = os.environ.get('AAIO_API_KEY')
    AAIO_MERCHANT_ID = os.environ.get('AAIO_MERCHANT_ID')
    SERVICE = 'aaio'

    order = Order.objects.get(id=order_id)
    if order.status:
        msg = f'{SERVICE}: Заказ оплачен'
        order.comment = msg
        order.save()
        logger.info(msg)
        return True

    params = {
        'merchant_id': AAIO_MERCHANT_ID,
        'order_id': order_id
    }
    headers = {
        'Accept': 'application/json',
        'X-Api-Key': AAIO_API_KEY
    }

    try:
        response = requests.post(url=AAIO_INFO, data=params, headers=headers, timeout=(15, 60))
    except ConnectTimeout:
        logger.error('ConnectTimeout')  # Не хватило времени на подключение к сайту
    except ReadTimeout:
        logger.error('ReadTimeout')  # Не хватило времени на выполнение запроса

    if response.status_code not in [200, 400, 401]:
        logger.error('Response code: ' + str(response.status_code))
        return True
    else:
        try:
            response_json = response.json()
        except Exception as e:
            logger.error(f'Не удалось пропарсить ответ: {e}')

        if response_json['type'] != 'success':
            logger.error('Ошибка: ' + response_json['message'])
            return True
        else:
            if response_json['status'] == 'expired':
                msg = f'{SERVICE}: Не оплачено, время заказа истекло в сервисе оплаты'
                order.comment = msg
                order.save()
                logger.info(msg)
                return True
            elif response_json['status'] == 'in_process':
                msg = f'{SERVICE}: Заказ в процессе оплаты, потребуется ручное подтверждение в сервисе оплаты aaio'
                order.comment = msg
                order.save()
                logger.info(msg)
                return True
            elif response_json['status'] == 'success' or response_json['status'] == 'hold':
                msg = f'{SERVICE}: Заказ оплачен'
                order.comment = msg
                order.save()
                logger.info(msg)
                data = {
                    'order_id': response_json['order_id'],
                    'amount': response_json['amount'],
                    'currency': response_json['currency'],
                    'merchant_id': response_json['merchant_id'],
                    'status': True,
                    'service': SERVICE
                }

                payload = json.dumps(data)

                with amqp.Connection(
                        host=f'{os.environ.get("RABBIT_HOST")}:{os.environ.get("RABBIT_PORT")}',
                        userid=os.environ.get("RABBIT_USER"),
                        password=os.environ.get("RABBIT_PASSWORD")
                ) as c:
                    ch = c.channel()
                    logger.info('Celery connected to rabbitmq')
                    ch.basic_publish(
                        amqp.Message(body=payload.encode()),
                        routing_key='payment-to-bot'
                    )
                    logger.info('Celery task was successfully sent to rabbitmq')
                return True
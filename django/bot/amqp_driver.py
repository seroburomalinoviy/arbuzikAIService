import pika
import aioamqp
import os

import logging

logger = logging.getLogger(__name__)


async def push_amqp_message(user_id):
    try:
        transport, protocol = await aioamqp.connect(
            host=os.environ.get('RABBIT_HOST'),
            port=os.environ.get('RABBIT_HOST'),
            login=os.environ.get('RABBIT_USER'),
            password=os.environ.get('RABBIT_PASSWORD'),
        )
    except aioamqp.AmqpClosedConnection:
        logger.error("AMQP closed connections")
        return

    channel = await protocol.channel()
    queue_name = "bot_rvc"
    payload = user_id
    exchange_name = ''
    await channel.queue_declare(queue_name)
    await channel.publish(payload, exchange_name, queue_name)

    #
    # credentials = pika.PlainCredentials(
    #     os.environ.get('RABBIT_USER'),
    #     os.environ.get('RABBIT_PASSWORD'))
    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(
    #         os.environ.get('RABBIT_HOST'),
    #         int(os.environ.get('RABBIT_PORT')
    #         ),
    #     '/', credentials, heartbeat=0, socket_timeout=7)
    # )
    # channel = connection.channel()
    # channel.queue_declare(queue='hello')
    # channel.basic_publish(exchange='',
    #                       routing_key='hello',
    #                       body=f'{command}')
    # connection.close()


async def amqp_start():
    transport, protocol = await aioamqp.connect(os.environ.get('RABBIT_HOST'), login_method="PLAIN")
    channel = await protocol.channel()

    await channel.queue_declare(queue_name='bot-rvc', arguments={'x-message-ttl': 3600000})

    await channel.basic_consume(push, queue_name='mentor_found_bot', no_ack=True)




async def rabbit_consumer():
    transport, protocol = await aioamqp.connect(os.environ.get('RABBIT_HOST'), login_method="PLAIN")
    channel = await protocol.channel()

    await channel.queue_declare(queue_name='hello', arguments={'x-message-ttl': 3600000})

    await channel.basic_consume(callback, queue_name='client_bot', no_ack=True)

    credentials = pika.PlainCredentials(
        os.environ.get('RABBIT_USER'),
        os.environ.get('RABBIT_PASSWORD'))
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            os.environ.get('RABBIT_HOST'),
            int(os.environ.get('RABBIT_PORT')
                ),
            '/', credentials, heartbeat=0, socket_timeout=7)
    )
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue='hello', on_message_callback = callback, auto_ack = True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
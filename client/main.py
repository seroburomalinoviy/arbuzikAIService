import logging
import os
import asyncio
from pathlib import Path
import aio_pika
import json

import async_timeout
from redis import asyncio as aioredis
from dotenv import load_dotenv
from time import perf_counter

from launch_rvc import starter_infer

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s >>> %(funcName)s(%(lineno)d)",
    datefmt="%Y-%m-%d %H:%M:%S"
)

load_dotenv()
logger = logging.getLogger(__name__)

infer_parameters = {
    # get VC first
    "model_name": "example.pth",
    "source_audio_path": "mysource/voice_for_test.wav",
    "output_file_name": "TEST_OUT.wav",
    "feature_index_path": "logs/test/kasparova.index",
    # Get parameters for inference
    "speaker_id": 0,
    "transposition": -2,
    "f0_method": "rmvpe", #harvest
    "crepe_hop_length": 160,
    "harvest_median_filter": 3,
    "resample": 0,
    "mix": 1,
    "feature_ratio": 0.95,
    "protection_amnt": 0.33,
    "protect1": 0.45,
    "DoFormant": False, # was True
    "Timbre": 8.0,
    "Quefrency": 1.2,
}


async def push_amqp_message(payload):
    try:
        connection = await aio_pika.connect_robust(
            host=os.environ.get('RABBIT_HOST'),
            port=int(os.environ.get('RABBIT_PORT')),
            login=os.environ.get('RABBIT_USER'),
            password=os.environ.get('RABBIT_PASSWORD'),
        )
    except aio_pika.exceptions.CONNECTION_EXCEPTIONS as e:
        logger.error(e.args[0])
        await asyncio.sleep(3)
        return await push_amqp_message(payload)
    except Exception as e:
        logger.error(e.args[0])
        await asyncio.sleep(3)
        return await push_amqp_message(payload)

    logger.info('Connected to rabbit')
    queue_name = "rvc-to-bot"
    routing_key = "rvc-to-bot"
    exchange_name = ''

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=True)

        await channel.default_exchange.publish(
            aio_pika.Message(body=payload.encode()),
            routing_key=routing_key,
        )
    logger.info(f'message {payload} sent to bot')


async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:

                    message = message.get("data").decode()

                    logger.info(f'\nGET MESSAGE FROM RABBIT\n{message}')

                    payload = json.loads(message)

                    user_id = payload.get('user_id')
                    chat_id = payload.get('chat_id')

                    infer_parameters['model_name'] = payload.get('voice_model_pth')
                    infer_parameters['feature_index_path'] = payload.get('voice_model_index')
                    infer_parameters['source_audio_path'] = os.environ.get('USER_VOICES_RAW_VOLUME') + '/' + payload.get('voice_filename')
                    infer_parameters['output_file_name'] = payload.get('voice_filename')
                    infer_parameters['transposition'] = payload.get('pitch')

                    logger.info(f"infer parameters: {infer_parameters['model_name']=},\n"
                                f" {infer_parameters['source_audio_path']=},\n"
                                f"{infer_parameters['output_file_name']=}\n"
                                f"{infer_parameters['feature_index_path']=}\n"
                                f"{infer_parameters['transposition']=}"
                                )

                    start = perf_counter()
                    starter_infer(**infer_parameters)
                    logger.info(f'finished for: {perf_counter() - start}')

                    payload = {
                        "user_id": user_id,
                        "chat_id": chat_id,
                        "voice_id": payload.get('voice_filename')
                    }
                    logger.info(payload)
                    try:
                        await push_amqp_message(json.dumps(payload))
                        logger.info('after')
                    except Exception as e:
                        logger.info(e)

                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass


async def main():
    logger.info(f'\nSTART MAIN\n')
    try:
        redis = aioredis.from_url(
            url=f"redis://{os.environ.get('REDIS_HOST')}",
        )
    except Exception as e:
        logger.info(f'[{type(e).__name__}] - {e}')

    pubsub = redis.pubsub()
    await pubsub.subscribe("channel:raw-data")
    logger.info(f'GET REDIS SUBSCRIBE')
    await asyncio.create_task(reader(pubsub))

if __name__ == "__main__":
    asyncio.run(main())




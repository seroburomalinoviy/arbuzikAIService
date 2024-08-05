import logging
import os
import asyncio
from pathlib import Path
import aio_pika
import json
import pika

import async_timeout
from redis import asyncio as aioredis
from dotenv import load_dotenv
from time import perf_counter

from launch_rvc import starter_infer

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


def _create_connection():
    credentials = pika.PlainCredentials(
        username=os.environ.get('RABBIT_USER'),
        password=os.environ.get('RABBIT_PASSWORD')
    )
    param = pika.ConnectionParameters(
        host=os.environ.get('RABBIT_HOST'),
        port=int(os.environ.get('RABBIT_PORT')),
        credentials=credentials,
    )
    return pika.BlockingConnection(param)


def convert_to_voice(input_path: str, output_path: str) -> None:
    """
    Creates a new file with `opus` format using `libopus` plugin. The new file can be recognized as a voice message by
    Telegram.

    :param input_path: str: The path of the input file
    :param output_path: str: The output path of the converted file
    """
    os.system(
        f"ffmpeg -y -i {input_path} -c:a libopus -b:a 32k -vbr on "
        f"-compression_level 10 -frame_duration 60 -application voip"
        f" {output_path}")


def push_amqp_message(payload):
    routing_key = "rvc-to-bot"

    with _create_connection() as connection:
        channel = connection.channel()
        logger.debug("message is publishing")
        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=json.dumps(payload).encode(),
        )

    logger.debug(f'message {payload} sent to bot')


async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:

                    message = message.get("data").decode()
                    payload = json.loads(message)

                    user_id = payload.get('user_id')
                    chat_id = payload.get('chat_id')
                    voice_name = payload.get('voice_name')
                    extension_ogg = payload.get('extension')
                    voice_raw_path = os.environ['USER_VOICES_RAW_VOLUME'] + '/' + voice_name + extension_ogg
                    voice_processed_path = os.environ['USER_VOICES_PROCESSED_VOLUME'] + '/' + voice_name
                    voice_ogg_path = os.environ['USER_VOICES_PROCESSED_VOLUME'] + '/' + voice_name + extension_ogg

                    infer_parameters['model_name'] = payload.get('voice_model_pth')
                    infer_parameters['feature_index_path'] = payload.get('voice_model_index')
                    infer_parameters['source_audio_path'] = voice_raw_path
                    infer_parameters['output_file_name'] = voice_name
                    infer_parameters['transposition'] = payload.get('pitch')

                    logger.info(f"infer parameters: {infer_parameters['model_name']=},\n"
                                f" {infer_parameters['source_audio_path']=},\n"
                                f"{infer_parameters['output_file_name']=}\n"
                                f"{infer_parameters['feature_index_path']=}\n"
                                f"{infer_parameters['transposition']=}"
                                )

                    start = perf_counter()

                    if not starter_infer(**infer_parameters):
                        continue

                    logger.info(f'NN finished for: {perf_counter() - start}')

                    convert_to_voice(voice_processed_path, voice_ogg_path)

                    logger.info(f'NN + Formatting finished for: {perf_counter() - start}')

                    payload = {
                        "user_id": user_id,
                        "chat_id": chat_id,
                        "voice_filename": voice_name + extension_ogg
                    }
                    logger.debug(payload)

                    push_amqp_message(payload)

                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass


async def main():
    logger.debug(f'\nSTART MAIN\n')
    try:
        redis = aioredis.from_url(
            url=f"redis://{os.environ.get('REDIS_HOST')}",
        )
    except Exception as e:
        logger.info(f'[{type(e).__name__}] - {e}')

    pubsub = redis.pubsub()
    await pubsub.subscribe("channel:raw-data")
    logger.debug(f'GET REDIS SUBSCRIBE')
    await asyncio.create_task(reader(pubsub))

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s >>> %(funcName)s(%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    asyncio.run(main())




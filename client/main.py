import logging
from logging.config import dictConfig
import os
import asyncio
import json
import pika

import async_timeout
import redis
import requests
from dotenv import load_dotenv
from time import perf_counter

from launch_rvc import starter_infer
import logging_config

logger = logging.getLogger(__name__)

load_dotenv()

infer_parameters = {
    # get VC first
    "model_name": None,  # "example.pth",
    "source_audio_path": None,  # "mysource/voice_for_test.wav",
    "output_file_name": None,  # "TEST_OUT.wav",
    "feature_index_path": None,  # "logs/test/kasparova.index",
    # Get parameters for inference
    "speaker_id": 0,
    "transposition": -2,
    "f0_method": "rmvpe",  # harvest
    "crepe_hop_length": 160,
    "harvest_median_filter": 3,
    "resample": 0,
    "mix": 1,
    "feature_ratio": 0.95,
    "protection_amnt": 0.33,
    "protect1": 0.45,
    "DoFormant": False,  # was True
    "Timbre": 8.0,
    "Quefrency": 1.2,
}


def _create_connection():
    credentials = pika.PlainCredentials(
        username=os.environ.get("RABBIT_USER"),
        password=os.environ.get("RABBIT_PASSWORD"),
    )
    param = pika.ConnectionParameters(
        host=os.environ.get("RABBIT_HOST"),
        port=int(os.environ.get("RABBIT_PORT")),
        credentials=credentials,
    )
    return pika.BlockingConnection(param)


def convert_to_voice(path):
    """
    Creates a new file with `opus` format using `libopus` plugin. The new file can be recognized as a voice message by
    Telegram.

    :param path:
    """
    os.system(
        f"ffmpeg -y -i {path + '.tmp'} -c:a libopus -b:a 32k -vbr on "
        f"-compression_level 10 -frame_duration 60 -application voip"
        f" {path}"
    )


def push_amqp_message(payload, routing_key="rvc-to-bot"):

    with _create_connection() as connection:
        channel = connection.channel()
        queue = channel.queue_declare(routing_key, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=json.dumps(payload).encode(),
        )

    logger.info(f"A message from RVC to BOT: \n{payload}")


async def reader(r: redis.Redis):
    while True:
        try:
            async with (async_timeout.timeout(1)):
                name_of_list = "raw-data"

                message_from_list = r.blpop([name_of_list])
                logger.info(f"{message_from_list=}")
                if message_from_list:

                    payload: dict = json.loads(message_from_list[1])

                    logger.info(f"Got payload: {payload}")

                    voice_name = payload.get('voice_name')
                    extension = payload.get('extension')
                    voice_filename = voice_name + extension
                    voice_path = os.environ["USER_VOICES"] + "/" + voice_filename

                    infer_parameters["model_name"] = payload.get('voice_model_pth')
                    infer_parameters["feature_index_path"] = payload.get('voice_model_index')
                    infer_parameters["source_audio_path"] = voice_path
                    infer_parameters["output_file_name"] = voice_filename + ".tmp" if extension == ".ogg" else voice_filename
                    infer_parameters["transposition"] = payload.get('pitch')

                    logger.info(
                        f"infer parameters: {infer_parameters['model_name']=},\n"
                        f" {infer_parameters['source_audio_path']=},\n"
                        f"{infer_parameters['output_file_name']=}\n"
                        f"{infer_parameters['feature_index_path']=}\n"
                        f"{infer_parameters['transposition']=}"
                    )

                    start = perf_counter()
                    success_flag = starter_infer(**infer_parameters)
                    if not success_flag:
                        payload["error"] = True
                    else:

                        logger.info(f"NN finished for: {perf_counter() - start}")

                        if extension == ".ogg":
                            convert_to_voice(voice_path)

                            time_per_task = float(perf_counter() - start)
                            logger.info(
                                f"NN + Formatting finished for: {time_per_task}"
                            )

                        response = requests.post('http://prometheus-server:9001/api/add_speed', json={"speed": time_per_task})
                        logger.info(f"Response from prometheus-server [add_speed]: {response.status_code}")

                        response = requests.get('http://prometheus-server:9001/api/complete_task')
                        logger.info(f"Response from prometheus-server [complete_task]: {response.status_code}")

                        payload["voice_filename"] = voice_filename
                        payload["error"] = False
                        logger.debug(payload)

                    push_amqp_message(payload)

        except asyncio.TimeoutError as e:
            logger.error(e)


async def main():
    host, port = os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT')
    try:
        r = redis.Redis(host=host, port=int(port), retry_on_timeout=True)
    except redis.exceptions.ConnectionError:
        logger.info(f"Redis ConnectionError: {host=} {port=}")
    except Exception as e:
        logger.info(f"Exception during Redis connection\n{e}")
    else:
        await asyncio.create_task(reader(r))


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    dictConfig(logging_config.config)
    logging.getLogger('pika').setLevel(logging.WARNING)

    asyncio.run(main())

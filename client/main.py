import logging
from logging.handlers import RotatingFileHandler
import os
import asyncio
import sys
import json
import pika

import async_timeout
import redis
from redis.exceptions import ConnectionError, DataError, NoScriptError, RedisError, ResponseError
from dotenv import load_dotenv
from time import perf_counter

from launch_rvc import starter_infer

load_dotenv()

infer_parameters = {
    # get VC first
    "model_name": "example.pth",
    "source_audio_path": "mysource/voice_for_test.wav",
    "output_file_name": "TEST_OUT.wav",
    "feature_index_path": "logs/test/kasparova.index",
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


def decode_dict(msg: dict, encoding_used='utf-8'):
    return {k.decode(encoding_used): v.decode(encoding_used) if isinstance(v, bytes) else decode_dict(v, encoding_used) for k, v in msg.items()}


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


def push_amqp_message(payload):
    routing_key = "rvc-to-bot"

    with _create_connection() as connection:
        channel = connection.channel()
        logging.debug("message is publishing")
        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=json.dumps(payload).encode(),
        )

    logging.debug(f"message {payload} sent to bot")


async def reader(r):
    while True:
        try:
            async with (async_timeout.timeout(1)):
                stream_key = 'raw-data'
                logging.info(f"The {stream_key} stream's length: {r.xlen(stream_key)}")
                stream_message = r.xread(count=1, streams={stream_key: '$'}, block=0)
                logging.info(f"{stream_message=}")
                if stream_message:
                    message_id = stream_message[0][1][0][0]
                    message: dict = stream_message[0][1][0][1]
                    payload: dict = decode_dict(message)

                    logging.info(f"Got payload: {payload}")

                    voice_name = payload.get('voice_name')
                    extension = payload.get('extension')
                    voice_filename = voice_name + extension
                    voice_path = os.environ["USER_VOICES"] + "/" + voice_filename

                    infer_parameters["model_name"] = payload.get('voice_model_pth')
                    infer_parameters["feature_index_path"] = payload.get('voice_model_index')
                    infer_parameters["source_audio_path"] = voice_path
                    infer_parameters["output_file_name"] = (
                        voice_filename + ".tmp"
                        if extension == ".ogg"
                        else voice_filename
                    )
                    infer_parameters["transposition"] = payload.get('pitch')

                    logging.debug(
                        f"infer parameters: {infer_parameters['model_name']=},\n"
                        f" {infer_parameters['source_audio_path']=},\n"
                        f"{infer_parameters['output_file_name']=}\n"
                        f"{infer_parameters['feature_index_path']=}\n"
                        f"{infer_parameters['transposition']=}"
                    )

                    start = perf_counter()
                    starter_infer(**infer_parameters)
                    logging.info(f"NN finished for: {perf_counter() - start}")

                    if extension == ".ogg":
                        convert_to_voice(voice_path)
                        logging.info(
                            f"NN + Formatting finished for: {perf_counter() - start}"
                        )

                    stream_key = 'processed-data'
                    r.xadd(stream_key, {
                            'complete_for': perf_counter() - start,
                            'duration': payload.get('duration'),
                            'count_task': r.xlen(stream_key),
                            'actual_count_tasks': r.xlen(stream_key) - r.xlen("raw-data")
                        }
                    )
                    # logging.info(message_id)
                    # r.xdel('raw-data', message_id)

                    payload["voice_filename"] = voice_filename
                    logging.debug(payload)

                    push_amqp_message(payload)

        except asyncio.TimeoutError as e:
            logging.error(e)


async def main():
    try:
        r = redis.Redis(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT'),
            retry_on_timeout=True
        )
    except ConnectionError as e:
        logging.error(e)
        sys.exit(1)
    except ResponseError as e:
        logging.error(e)
        sys.exit(1)
    except RedisError as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error(e)
        sys.exit(1)

    await asyncio.create_task(reader(r))


if __name__ == "__main__":
    os.makedirs('/logs', exist_ok=True)
    rotating_handler = RotatingFileHandler('/logs/client.log', backupCount=5, maxBytes=512 * 1024)
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s >>> %(funcName)s(%(lineno)d)"
    formatter = logging.Formatter(log_format)
    rotating_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger('').addHandler(rotating_handler)

    asyncio.run(main())

import logging
import os
import asyncio
from pathlib import Path

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


async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    logger.info(f'\nGET MESSAGE FROM RABBIT\n{message.get("data").decode()=}')
                    # call Mangio-RVC

                    voice_filename, pitch, voice_model_pth, voice_model_index, extension = message.get("data").decode().split('__')
                    # await find_model_files(voice_model_path)

                    infer_parameters['model_name'] = voice_model_pth
                    infer_parameters['feature_index_path'] = voice_model_index
                    infer_parameters['source_audio_path'] = os.environ.get('USER_VOICES_RAW_VOLUME') + '/' + voice_filename + extension
                    infer_parameters['output_file_name'] = voice_filename + extension
                    infer_parameters['transposition'] = pitch

                    logger.info(f"infer parameters: {infer_parameters['model_name']=},\n"
                                f" {infer_parameters['source_audio_path']=},\n"
                                f"{infer_parameters['output_file_name']=}\n"
                                f"{infer_parameters['feature_index_path']=}\n"
                                f"{infer_parameters['transposition']=}"
                                )

                    start = perf_counter()
                    starter_infer(**infer_parameters)
                    logger.info(f'finished for: {perf_counter() - start}')

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




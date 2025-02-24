import os
from dotenv import load_dotenv

from infer_web_without_cli import vc_single, get_vc
from my_utils import load_audio, CSVutil
import scipy.io.wavfile as wavfile

import logging

logger = logging.getLogger(__name__)

load_dotenv()


def starter_infer(
    model_name: str,
    source_audio_path: str,
    output_file_name: str,
    feature_index_path: str,
    speaker_id: int,
    transposition: float,
    f0_method: str,
    crepe_hop_length: int,
    harvest_median_filter: int,
    resample: int,
    mix: float,
    feature_ratio: float,
    protection_amnt: float,
    protect1: float = 0.5,
    DoFormant: bool = False,
    Timbre: float = 0.0,
    Quefrency: float = 0.0,
):
    if not DoFormant:
        Quefrency = 0.0
        Timbre = 0.0
        CSVutil(
            "csvdb/formanting.csv", "w+", "formanting", DoFormant, Quefrency, Timbre
        )
    else:
        CSVutil(
            "csvdb/formanting.csv", "w+", "formanting", DoFormant, Quefrency, Timbre
        )

    logger.info("[Mangio-RVC] starter_infer: Starting the inference...")
    try:
        get_vc(model_name, protection_amnt, protect1)
    except Exception as e:
        logger.error(f"[Mangio-RVC] {e}")
        return
    logger.info("[Mangio-RVC] starter_infer: Performing inference...")

    msg, conversion_data = vc_single(
        speaker_id,
        source_audio_path,
        source_audio_path,
        transposition,
        None,
        f0_method,
        feature_index_path,
        feature_index_path,
        feature_ratio,
        harvest_median_filter,
        resample,
        mix,
        protection_amnt,
        crepe_hop_length,
    )

    if conversion_data is None:
        logger.error(f"[Mangio-RVC] Error: {msg} ")
        return
    elif isinstance(conversion_data, tuple):
        tgt_sr, audio_opt = conversion_data
        if tgt_sr is None and audio_opt is None:
            logger.error(f"[Mangio-RVC] Error: {msg} ")
            return
    else:
        logger.info(f"[Mangio-RVC] INFO: {msg}")
        tgt_sr, audio_opt = conversion_data
        logger.info(
            "[Mangio-RVC] starter_infer: Inference succeeded. Writing to %s/%s..."
            % ("audio-outputs", output_file_name)
        )
        try:
            result_path = os.environ.get("USER_VOICES")
            wavfile.write(
                "%s/%s" % (result_path, output_file_name),
                tgt_sr,
                audio_opt,
            )
            return True
        except Exception as e:
            logger.error(f"[wavfile error] {e}")

        logger.info(
            "[Mangio-RVC] starter_infer: Finished! Saved output to %s/%s"
            % (result_path, output_file_name)
        )

import os
from dotenv import load_dotenv

from infer_web_without_cli import vc_single, get_vc
from my_utils import load_audio, CSVutil
import scipy.io.wavfile as wavfile

import logging

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

    logging.info("[Mangio-RVC] starter_infer: Starting the inference...")
    try:
        vc_data = get_vc(model_name, protection_amnt, protect1)
    except Exception as e:
        logging.error(f"[vc_data error] {e}")
    logging.info("[Mangio-RVC] starter_infer: Performing inference...")

    try:
        conversion_data = vc_single(
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
    except Exception as e:
        logging.error(f"[vc_single error] {e}")

    if "Success." in conversion_data[0]:
        logging.info(
            "[Mangio-RVC] starter_infer: Inference succeeded. Writing to %s/%s..."
            % ("audio-outputs", output_file_name)
        )
        try:
            result_path = os.environ.get("USER_VOICES")
            wavfile.write(
                "%s/%s" % (result_path, output_file_name),
                conversion_data[1][0],
                conversion_data[1][1],
            )
        except Exception as e:
            logging.error(f"[wavfile error] {e}")

        logging.info(
            "[Mangio-RVC] starter_infer: Finished! Saved output to %s/%s"
            % (result_path, output_file_name)
        )
    else:
        logging.info(
            "[Mangio-RVC] starter_infer: Inference failed. Here's the traceback: "
        )
        logging.info(conversion_data[0])

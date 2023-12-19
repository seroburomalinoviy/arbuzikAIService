from infer_web import vc_single, get_vc
from my_utils import load_audio, CSVutil
import scipy.io.wavfile as wavfile

import logging

logger = logging.Logger(__name__)


infer_parameters = {
    # get VC first
    "model_name": "kasparova_by_Nstudio.pth",
    "source_audio_path": "mysource/voice_for_test.wav",
    "output_file_name": "TEST_OUT.wav",
    "feature_index_path": "logs/test/kasparova.index",
    # Get parameters for inference
    "speaker_id": 0,
    "transposition": -2,
    "f0_method": "harvest",
    "crepe_hop_length": 160,
    "harvest_median_filter": 3,
    "resample": 0,
    "mix": 1,
    "feature_ratio": 0.95,
    "protection_amnt": 0.33,
    "protect1": 0.45,
    "DoFormant": True,
    "Timbre": 8.0,
    "Quefrency": 1.2,
}


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
        vc_data = get_vc(model_name, protection_amnt, protect1)
    except Exception as e:
        logger.error(f"[vc_data error] {e.__name__}\n{e}")
    logger.info(vc_data)
    logger.info("[Mangio-RVC] starter_infer: Performing inference...")

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
        logger.error(f"[vc_single error] {e.__name__}\n{e}")

    if "Success." in conversion_data[0]:
        logger.info(
            "[Mangio-RVC] starter_infer: Inference succeeded. Writing to %s/%s..."
            % ("audio-outputs", output_file_name)
        )
        try:
            wavfile.write(
                "%s/%s" % ("audio-outputs", output_file_name),
                conversion_data[1][0],
                conversion_data[1][1],
            )
        except Exception as e:
            logger.error(f"[wavfile error] {e.__name__}\n{e}")
        logger.info(
            "[Mangio-RVC] starter_infer: Finished! Saved output to %s/%s"
            % ("audio-outputs", output_file_name)
        )

    else:
        logger.info(
            "[Mangio-RVC] starter_infer: Inference failed. Here's the traceback: "
        )
        logger.info(conversion_data[0])


starter_infer(**infer_parameters)

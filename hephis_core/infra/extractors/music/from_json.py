
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action
from hephis_core.services.detectors.chord_detector import ChordDetector

@log_action(action="extract_music_from_json")
@extractor(domain="music", input_type="json")
def extract_music_from_json_music(obj: dict) -> dict | None:
    return ChordDetector.detect(obj, "json")
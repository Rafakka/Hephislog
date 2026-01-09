
from hephis_core.infra.extractors.registry import extractor
from hephis_core.services.detectors.chord_detector import ChordDetector

@extractor(domain="music", input_type="json")
def extract_music_from_json(obj: dict) -> dict | None:
    return ChordDetector.detect(obj, "json")
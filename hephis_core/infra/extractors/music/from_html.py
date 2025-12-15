from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action

@log_action(action="extract_music_from_html")
@extractor(domain="music", input_type="html")
def extract_music_from_html(html: str) -> dict | None:
    if not isinstance(html, str):
        return None

    return ChordDetector.detect(html, "html")
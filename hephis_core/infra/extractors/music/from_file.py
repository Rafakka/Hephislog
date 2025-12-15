import json
from pathlib import Path
from hephis_core.services.detectors.raw_detectors import (
    is_html, is_json, is_text
)
from .from_html import extract_music_from_html
from .from_json import extract_music_from_json
from .from_text import extract_music_from_text
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action


@log_action(action="extract_music_from_file")
@extractor(domain="music", input_type="file")
def extract_music_from_file(path: str) -> dict | None:
    file_path = Path(path)

    if not file_path.exists() or not file_path.is_file():
        return None
    
    content = file_path.read_text(errors="ignore")

    if is_html(content):
        return extract_music_from_html(content)
    
    try:
        obj = json.loads(content)
        raw = extract_music_from_json(obj)
        if raw:
            return raw
    except:
        pass

    return extract_music_from_text(content)
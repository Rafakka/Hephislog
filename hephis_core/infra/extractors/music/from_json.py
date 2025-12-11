
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action

@log_action(action="extract_music_from_json")
@extractor(domain="music", input_type="json")
def extract_music_from_json(obj:dict)-> dict | None:

    if not isinstance(obj, dict):
        return None

    if "paragraphs" in obj and "title" in obj:
        return {
            "title":obj["title"],
            "paragraphs":obj["paragraphs"],
            "source":"json_raw"
        }

    return None


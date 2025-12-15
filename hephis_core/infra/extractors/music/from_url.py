from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action
import requests

@log_action(action="extract_music_from_url")
@extractor(domain="music", input_type="url")
def extract_music_from_url(url: str):

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception:
        return None

    return response.text
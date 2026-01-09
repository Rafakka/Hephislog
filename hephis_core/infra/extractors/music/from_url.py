import requests
from typing import Optional
from hephis_core.infra.extractors.registry import extractor

@extractor(domain="*",input_type="url")
def extract_music_from_url(url:str) -> Optional[str]:
        return None
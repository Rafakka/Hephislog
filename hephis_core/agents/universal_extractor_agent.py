from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer
from hephis_core.infra.extractors.validators.music_validator import is_valid_music
from hephis_core.infra.extractors.validators.recipe_validator import is_valid_recipe
from .from_url import extract_recipe_from_url
from .from_html import extract_recipe_from_html
from .from_url import extract_music_from_url
from .from_html import extract_music_from_html
from .from_file import extract_music_from_file
from .form_json import extract_music_from_json
from .from_text import extract_music_from_text


class UniversalExtractorAgent:

    extractor_registry = {
        "url": {"recipe":extract_recipe_from_url,
                "music":extract_music_from_url},
        "html":{"recipe":extract_recipe_from_html,
                "music":extract_music_from_html},
        "json":{"recipe":extract_recipe_from_json,
                "music":extract_music_from_json},
        "text":{"recipe":extract_recipe_text,
                "music":extract_music_from_text},
        "file":{"recipe":extract_recipe_from_file,
                "music":extract_music_from_file}
    }

    validators = {
        "recipe": is_valid_recipe,
        "music": is_valid_music
    }

    def extract_any(input_value, input_type):
        extractors = extractor_registry[input_type]
        for domain, extractor_fn in extractors.items():
            raw=extractor_fn(input_value)
            if raw is None:
                continue
            validator = validators.get(domain)
            if validator and validator(raw):
                return domain, raw
        return "system", None

    @on_event("system.xxx_received")
    def handle_input(payload):
        input = payload["data"]
        type = payload["type"]
        domain, raw = extract_any(input, type)
        emit(f"{domain}.raw_extracted")


    
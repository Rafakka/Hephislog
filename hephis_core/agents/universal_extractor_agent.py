from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer
from hephis_core.infra.extractors.registry import EXTRACTOR_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC

class UniversalExtractorAgent:

    validators = {
    "recipe": RECIPE,
    "music": MUSIC
    }

    def emit_result(self, domain, raw, source_info):
        announcer.emit(f"{domain}.raw_extracted", {
            "raw": raw,
            "source": source_info
        })

    def extract_any(self, input_value, input_type):
        extractors = EXTRACTOR_REGISTRY.get(input_type, {})
        for domain, extractor_functions in extractors.items():
            for fn in extractor_functions:
                try:
                    raw = fn(input_value)
                except Exception as exc:
                    continue
                if raw is None:
                    continue
                validator = self.validators.get(domain)
                if validator and validator(raw):
                    return domain, raw
        return "system", None

    @on_event("system.*_received")
    def handle_input(self, payload):
        input_value = payload["data"]
        input_type  = payload["type"]
        domain, raw = self.extract_any(input_value, input_type)
        self.emit_result(domain, raw, input_value)
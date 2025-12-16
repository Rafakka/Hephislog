from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import EventBus
from hephis_core.infra.extractors.registry import EXTRACTOR_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC

class UniversalExtractorAgent:

    validators = {
        "recipe": RECIPE,
        "music": MUSIC
    }

    def emit_result(self, raw, source_info):
        EventBus.emit(
            "system.extraction.completed",
            {
                "raw": raw,
                "source": source_info
            }
        )

    def extract_any(self, input_value, input_type, debug=False):

        extractors = EXTRACTOR_REGISTRY.get(input_type, {})

        if debug:
            print(f"[PRIMARY] Trying {fn.__name__} for domain {domain}")

        for domain, extractor_functions in extractors.items():
            for fn in extractor_functions:
                try:
                    raw = fn(input_value)
                    if raw is None:
                        continue
                except Exception:
                    continue
                validator = self.validators.get(domain)
                if validator and validator(raw):
                    return domain, raw

        html_content = to_html(input_value, input_type)
        html_extractors = EXTRACTOR_REGISTRY.get("html",{})

        if debug:
            print("[FALLBACK] Converting to HTML…")

        for domain, extractor_functions in html_extractors.items():
            for fn in extractor_functions:
                try:
                    raw = fn(html_content)
                    if raw is None:
                        continue
                except Exception:
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
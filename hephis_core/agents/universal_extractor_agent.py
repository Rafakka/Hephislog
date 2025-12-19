from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.utils.logger_decorator import log_action
from hephis_core.infra.extractors.registry import EXTRACTOR_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC

class UniversalExtractorAgent:

    validators = {
        "recipe": RECIPE,
        "music": MUSIC
    }

    def emit_result(self, raw, domain, run_id,source):
        event_bus.emit(
            "system.extraction.completed",
            {   
                "raw":raw,
                "domain":domain,
                "run_id": run_id,
                "source":source,
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
    @log_action(action="agt-extracting-payload")
    def handle_input(self, payload):
        input_value = payload["data"]
        input_type  = payload["type"]
        run_id = payload["run_id"]
        source = payload["source"]

        domain, raw = self.extract_any(input_value, input_type)
        self.emit_result(raw, domain,run_id,source)
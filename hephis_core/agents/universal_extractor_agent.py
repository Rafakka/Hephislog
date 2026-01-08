from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.infra.extractors.registry import EXTRACTOR_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class UniversalExtractorAgent:

    def __init__(self):
        print("4 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    validators = {
        "recipe": RECIPE,
        "music": MUSIC
    }

    def emit_result(self, raw, domain, run_id, source):
        run_context.touch(
                run_id,
                agent="UniversalExtractorAgent",
                action="extracted_file",
                domain=domain,
                reason="valid_file_type",
            )
        run_context.emit_fact(
                run_id,
                stage="extractor",
                component="UniversalExtractorAgent",
                result="accepted",
                reason="valid_file_type",
                )
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
        source = payload.get("source")
        run_id = extract_run_id(payload)

        if not run_id:
            logger.warning("Source file has no valid id or run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"extraction-by-universal-extractor",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        domain, raw = self.extract_any(input_value, input_type)

        if not domain or not raw:
            run_context.touch(
                run_id,
                agent="UniversalExtractorAgent",
                action="extract_file",
                reason="no_domain_or_and_no_raw",
            )
            run_context.emit_fact(
                    run_id,
                    stage="extractor",
                    component="UniversalExtractorAgent",
                    result="declined",
                    reason="no_domain_or_and_no_raw",
                    )
            return

        self.emit_result(raw, domain,run_id,source)
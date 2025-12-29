from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.infra.retrievers.registry import RETRIEVER_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC
from hephis_core.utils.logger_decorator import log_action

class UniversalRetrieverAgent:

    def __init__(self):
        for att_name in dir(self):
            attr = getattr(self, att_name)
            if callable(attr) and hasattr(attr, "_event_name"):
                event_bus.subscribe(attr._event_name, attr)

    validators = {
        "recipe": RECIPE,
        "music": MUSIC
    }

    def emit_result(self, domain, data, source_info):
        event_bus.emit(
            f"{domain}.retrieved",
            {
                "data": data,
                "source": source_info
            }
        )

    def extract_any(self, input_value, input_type):
        extractors = RETRIEVER_REGISTRY.get(input_type, {})

        for domain, extractor_functions in extractors.items():
            for fn in extractor_functions:
                try:
                    result = fn(input_value)
                except Exception:
                    continue

                if result is None:
                    continue

                validator = self.validators.get(domain)
                if validator and validator(result):
                    return domain, result

        return "system", None
        
    @log_action(action="agt-retriving-data-api")
    @on_event("system.*api_requested")
    def handle_input(self, payload):
        input_value = payload["data"]
        input_type  = payload["type"]

        domain, data = self.extract_any(input_value, input_type)
        self.emit_result(domain, data, input_value)
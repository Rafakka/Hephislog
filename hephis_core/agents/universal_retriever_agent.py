from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import EventBus
from hephis_core.infra.retrievers.registry import RETRIEVER_REGISTRY
from hephis_core.infra.retrievers.validators import RECIPE, MUSIC
from hephis_core.utils.logger_decorator import log_action

class UniversalRetrieverAgent:

    validators = {
        "recipe": RECIPE,
        "music": MUSIC
    }

    def emit_result(self, domain, data, source_info):
        EventBus.emit(
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

    @on_event("system.*api_requested")
    @log_action(action="agt-retriving-data-api")
    def handle_input(self, payload):
        input_value = payload["data"]
        input_type  = payload["type"]

        domain, data = self.extract_any(input_value, input_type)
        self.emit_result(domain, data, input_value)
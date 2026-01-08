from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.infra.retrievers.registry import RETRIEVER_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC


class UniversalRetrieverAgent:

    def __init__(self):
        print("11 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

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
        
    @on_event("system.*api_requested")
    def handle_input(self, payload):
        input_value = payload["data"]
        input_type  = payload["type"]

        domain, data = self.extract_any(input_value, input_type)
        self.emit_result(domain, data, input_value)
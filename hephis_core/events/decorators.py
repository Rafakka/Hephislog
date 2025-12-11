
from .registry import exact_handlers, wildcard_handlers

class EventBus:
    def emit(self, event_name, payload):
        for fn in exact_handlers.get(event_name, []):
            fn(payload)

        for pattern, handlers in wildcard_handlers.items():
            if self.matches(pattern, event_name):
                for fn in handlers:
                    fn(payload)

from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus
from hephis_core.services.detectors.raw_detectors import detect_raw_type

class IdentifierAgent:

    @on_event("system.input_received")
    def handle_input(self, payload):

        incoming = payload["input"]
        raw_type = detect_raw_type(incoming)

        event_bus.emit(f"system.{raw_type}_received", {
            "data": incoming,
            "type": raw_type
        })
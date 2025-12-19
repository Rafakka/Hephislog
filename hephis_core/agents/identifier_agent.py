
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.services.detectors.raw_detectors import detect_raw_type
from hephis_core.utils.logger_decorator import log_action

class IdentifierAgent:

    @on_event("system.input_received")
    @log_action(action="agt-indentifing-obj-received")
    def handle_input(self, payload):

        incoming = payload["input"]
        raw_type = detect_raw_type(incoming)

        event_bus.emit(f"system.{raw_type}_received", {
            "data": incoming,
            "type": raw_type
        })
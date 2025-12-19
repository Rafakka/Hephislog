
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.services.detectors.raw_detectors import detect_raw_type
from hephis_core.utils.logger_decorator import log_action
import hephis_core.agents.decision_agent

@on_event("system.input_received")
@log_action("agt-identifies-input")
def identify_input(payload):
    incoming = payload["input"]
    source = payload["source"]
    raw_type = detect_raw_type(incoming)

    event_bus.emit(
        f"system.{raw_type}_received",
        {
            "data": incoming,
            "type": raw_type,
            "run_id": payload["run_id"],
            "source": source,
        }
    )
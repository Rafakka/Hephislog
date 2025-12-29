
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.services.detectors.raw_detectors import detect_raw_type
from hephis_core.utils.logger_decorator import log_action
import hephis_core.agents.decision_agent
from hephis_core.environment import ENV

class IdentifierAgent:
    
    def __init__(self):
        print("INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @log_action("agt-identifies-input")
    @on_event("system.input_received")
    def identify_input(self,payload):
        incoming = payload["input"]
        source = payload["source"]
        raw_type = detect_raw_type(incoming, ENV)

        event_bus.emit(
            f"system.{raw_type}_received",
            {
                "data": incoming,
                "type": raw_type,
                "run_id": payload["run_id"],
                "source": source,
            }
        )
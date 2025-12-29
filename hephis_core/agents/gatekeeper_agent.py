from hephis_core.events.event_bus import event_bus
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.decorators import on_event

class GatekeeperAgent:

    def __init__(self):
        for att_name in dir(self):
            attr = getattr(self, att_name)
            if callable(attr) and hasattr(attr, "_event_name"):
                event_bus.subscribe(attr._event_name, attr)

    @log_action(action="gatekeeper-announces")
    @on_event("system.external_input")
    def gatekeeper_process(self,payload):
        event_bus.emit(
            "system.input_received",
            {
                "input": payload["input"],
                "run_id": payload["run_id"],
                "source": "gatekeeper",
            }
        )
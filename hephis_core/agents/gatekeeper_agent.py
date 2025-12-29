from hephis_core.events.event_bus import event_bus
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.decorators import on_event

class GatekeeperAgent:

    @on_event("system.external_input")
    @log_action(action="gatekeeper-announces")
    def gatekeeper_process(payload):
        event_bus.emit(
            "system.input_received",
            {
                "input": payload["input"],
                "run_id": payload["run_id"],
                "source": "gatekeeper",
            }
        )
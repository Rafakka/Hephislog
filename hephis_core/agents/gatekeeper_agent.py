from hephis_core.events.event_bus import event_bus
from hephis_core.utils.logger_decorator import log_action

class GatekeeperAgent:

    @log_action(action="gatekeeper-announces")
    def process(self, incoming, run_id):
        event_bus.emit(
            "system.input_received",
            {
                "input": incoming,
                "run_id": run_id,
                "source": "gatekeeper",
            }
        )
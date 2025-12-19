from hephis_core.events.event_bus import EventBus
from hephis_core.utils.logger_decorator import log_action

class GatekeeperAgent:

    @log_action(action="gatekeeper-announces")
    def process(self, incoming):
        EventBus.emit(
            "system.input_received",
            {"input": incoming}
        )
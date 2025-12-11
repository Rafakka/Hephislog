from hephis_core.events.event_bus import event_bus

class GatekeeperAgent:

    def process(self, incoming):
        event_bus.emit(
            "system.input_received",
            {"input": incoming}
        )
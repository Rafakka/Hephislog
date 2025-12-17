from hephis_core.events.event_bus import EventBus

class GatekeeperAgent:

    def process(self, incoming):
        EventBus.emit(
            "system.input_received",
            {"input": incoming}
        )
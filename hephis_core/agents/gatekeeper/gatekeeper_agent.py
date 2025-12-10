
from hephis_core.events.registry import event_bus as announcer

class GatekeeperAgent:

    def __init__(self, announcer):
        self.announcer = announcer

    def process(self, incoming):
        self.announcer.announce(
            domain="system",
            action="input_received",
            data={"input":incoming}
        )
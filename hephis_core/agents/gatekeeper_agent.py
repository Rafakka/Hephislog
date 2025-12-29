from hephis_core.events.bus import event_bus
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.decorators import on_event

class GatekeeperAgent:

    def __init__(self):
        print("INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
        
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
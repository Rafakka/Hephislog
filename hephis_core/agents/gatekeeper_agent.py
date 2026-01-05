from hephis_core.events.bus import event_bus
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context

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

        run_id = payload.get("run_id")

        run_context.touch(
        run_id, 
        agent="GatekeeperAgent", 
        action ="saw_input", 
        event="system,input_received"
        )

        event_bus.emit(
            "system.input_received",
            {
                "input": payload["input"],
                "run_id": run_id,
                "source": "gatekeeper",
            }
        )
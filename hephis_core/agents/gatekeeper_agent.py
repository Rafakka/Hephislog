from hephis_core.events.bus import event_bus
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.agents.reporter_rules.base import logger

class GatekeeperAgent:

    def __init__(self):
        print("2 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
        
    @log_action(action="gatekeeper-announces")
    @on_event("system.external_input")
    def gatekeeper_process(self,payload):

        run_id = extract_run_id(payload)

        if not run_id:
            logger.warning("Source file has no valid id or run_id"),
            extra={
                    "agent":self.__class__.__name__,
                    "event":"reception-by-gate-keeper",
                    "payload":payload,
                }
            return

        run_context.touch(
        run_id, 
        agent="GatekeeperAgent", 
        action ="received_input", 
        event="system.external_input"
        )

        run_context.emit_fact(
            run_id,
            stage="gatekeeper",
            component="GatekepperAgent",
            result="accepted",
            reason="valid_external_input"
        )

        event_bus.emit(
            "system.input_received",
            {
                "input": payload,
                "run_id": run_id,
                "source": "gatekeeper",
            }
        )
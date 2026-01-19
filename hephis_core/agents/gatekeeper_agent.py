from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class GatekeeperAgent:

    def __init__(self):
        print("2 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
        
    @on_event("system.external_input")
    def gatekeeper_process(self,payload):
        print("RAN:",self.__class__.__name__) 

        run_id = extract_run_id(payload)
        raw = payload.get("raw")
        source = payload.get("source")
        domain_hint = payload.get("domain_hint")
        smells = payload.get("smells")

        print(smells)

        if not run_id:
            logger.warning("Source file has no valid id or run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"reception-by-gatekeeper",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
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
            "system.input_to_be_identified",
            {
                "input": payload,
                "raw":raw,
                "run_id": run_id,
                "source": source,
                "domain_hint":domain_hint,
                "smells":smells,
            }
        )
        return

from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.services.detectors.raw_detectors import detect_raw_type
from hephis_core.swarm.run_context import run_context
import hephis_core.agents.decision_agent
from hephis_core.environment import ENV
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class IdentifierAgent:
    
    def __init__(self):
        print("3 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.input_to_be_identified")
    def identify_input(self,payload):
        print("RAN:",self.__class__.__name__) 
        
        raw = payload.get("raw") or payload.get("input")
        source = payload.get("source")
        run_id = extract_run_id(payload)

        if not run_id:
            logger.warning("Source file has no valid id or run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"identifing-agent",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        raw_type = detect_raw_type(raw, ENV)

        print(f"CONTENTS OF DETECTION:--{raw_type}")

        if raw_type in (None, "unknown"):
            logger.warning("Source file has not being identified",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"identifing-agent",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            run_context.emit_fact(
                run_id,
                stage="identify",
                component="IdentifierAgent",
                result="declined",
                reason="raw_type_unkown"
            )
            return

        run_context.touch(
            run_id, 
            agent="IdentifierAgent", 
            action ="identified_type_of_file", 
            event="system.input_received"
        )

        run_context.emit_fact(
            run_id,
            stage="identify",
            component="IdentifierAgent",
            result="accepted",
            reason="valid_input_file"
        )
        
        event_bus.emit(
            f"system.input_identified",
            {
                "run_id":run_id,
                "raw":raw,
                "raw_type":raw_type,
                "source":source,
                "domain_hint":payload.get("domain_hint"),
            }
        )
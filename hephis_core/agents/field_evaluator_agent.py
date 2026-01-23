from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.environment import ENV
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class FieldEvaluatorAgent:
    
    def __init__(self):
        print("3 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.input_to_be_evaluated")
    def evaluate_fields(self,payload):
        print("RAN:",self.__class__.__name__) 

        raw = payload.get("raw") or payload.get("input")
        source = payload.get("source")
        run_id = extract_run_id(payload)
        smells = payload.get("smells")

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
        
        profile = FieldEvaluatorCore.evaluate(raw)

        if not profile:
            logger.warning("Source failed to be avaliated",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"identifing-agent",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return
    
        run_context.touch(
            run_id, 
            agent="FieldEvaluatorAgent", 
            action ="identified_fields_in_file", 
            event="system.input_to_be_evaluated"
        )

        run_context.emit_fact(
            run_id,
            stage="separation-of-fields",
            component="FieldEvaluatorAgent",
            result="accepted",
            reason="valid_file_type"
        )
        
        print(smells)

        event_bus.emit(
            f"system.input_identified",
            {
                "run_id":run_id,
                "raw":raw,
                "raw_type":raw_type,
                "source":source,
                "smells":smells,
                "content_profile":profile,
            }
        )
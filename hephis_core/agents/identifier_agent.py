
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
    
    def __init__(self, identifier_core):
        print("3 - INIT:",self.__class__.__name__)
        self.identifier_core = identifier_core
        print("* -  IDENTIFIER CORE - RUNNING")
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.input_to_be_identified")
    def identify_input(self,payload):
        print("RAN:",self.__class__.__name__) 

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

        smells = payload.get("smells")

        if not smells:
            logger.warning("Source file has no valid smell",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"identifing-agent",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        raw = payload.get("raw") or payload.get("input")

        if not raw:
            logger.warning("Source file has no valid raw",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"identifing-agent",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        source = payload.get("source")

        if not source:
            logger.warning("Source file has no source",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"identifing-agent",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return
        

        belief = self.identifier_core.evaluate(raw,smells)

        print("BELIEFS: ", belief)

        raw_type = belief["beliefs"]
        ranked = belief["ranked"]
        primary = ranked[0][0] if ranked else None
        
        confidence = smells.confidence

        print("BELIEFS: ", raw_type)
        print("RANKED :", ranked)

        if not raw_type:
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
        
        print(smells)

        event_bus.emit(
            f"system.input_identified",
            {
                "run_id":run_id,
                "raw":raw,
                "raw_type":raw_type,
                "source":source,
                "smells":smells,
                "confidence":confidence,
                "cleaning_strategy":payload.get("cleaning_strategy"),
            }
        )
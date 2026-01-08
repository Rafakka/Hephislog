from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.decision_store import decision_store
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class DecisionAgent:

    def __init__(self):
        print("5 - INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
                print("SUBCRIBING:", fn.__event_name__,"->",attr)

    @on_event("system.smells.post.extraction")
    def decide(self, payload):
        print("DECISION AGENT CALLED")
        smells = payload["smells", {}]
        run_id = extract_run_id(payload)
        source = payload.get("source")
        raw = payload["raw"]

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"decision-making",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return

        if not smells:
            logger.warning("smells are missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"decision-making",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return

        domain, confidence = max(smells.items(), key=lambda x: x[1])

        if confidence < 0.6:
            print(f"DECLINED: confidence too low ({confidence})")
            run_context.touch(
                run_id,
                agent="DecisionAgent",
                action="declined",
                domain=domain,
                reason="confidence low",
                confidence=confidence,
            )
            run_context.emit_fact(
            run_id,
            stage="decision",
            component="DecisionAgent",
            result="declined",
            reason="low_confidence",
            )
            return


        decision = {
            "domain": domain,
            "confidence": confidence,
            "smells": smells,
            "run_id": run_id,
            "source":source,
        }

        decision_store.store(run_id, decision)

        print("DECISION STORED:", decision)
        run_context.touch(
                run_id,
                agent="DecisionAgent",
                action="stored",
                domain=domain,
                reason="Normal flow",
                decision=decision,
            )
        run_context.emit_fact(
            run_id,
            result="stored",
            stage="decision",
            component="DecisionAgent",
            reason="decision made",
            )    
        
        if raw is None:
            run_context.touch(
                run_id,
                agent="DecisionAgent",
                action="Returned none",
                domain=domain,
                reason="No raw payload",
            )
            run_context.emit_fact(
            run_id,
            stage="decision",
            component="DecisionAgent",
            result="declined",
            reason="no_raw_payload"
            )
            return

        run_context.touch(
                run_id,
                agent="DecisionAgent",
                action="organized",
                domain=domain,
                reason="Processed",
                confidence=confidence,
            )
        run_context.emit_fact(
            run_id,
            stage="decision",
            component="DecisionAgent",
            result="organized",
            reason="matching context"
            )

        event_bus.emit(
                    f"intent.organize.{domain}",
                    {
                    "domain":domain,
                    "confidence":confidence,
                    "run_id":run_id,
                    "raw":raw,
                    "source":source,
                    }
                )
    
    @on_event("confidence.updated")
    def update_confidence(self, payload):
        key = (payload["smell"], payload["intent"])
        self.confidence[key] = payload["trust"]

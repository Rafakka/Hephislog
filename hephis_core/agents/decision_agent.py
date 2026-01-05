from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.utils.logger_decorator import log_action
from hephis_core.swarm.decision_store import decision_store
from hephis_core.swarm.run_context import run_context

class DecisionAgent:

    def __init__(self):
        print("INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
                print("SUBCRIBING:", fn.__event_name__,"->",attr)

    @log_action(action="agt-deciding-by-smell")
    @on_event("system.smells.post.extraction")
    def decide(self, payload):
        print("DECISION AGENT CALLED")
        smells = payload.get("smells", {})
        run_id = payload.get("run_id") or payload.get("id")
        source = payload.get("source")
        raw = payload.get("raw")

        if not smells or not run_id:
            run_context.touch(
                run_id,
                agent="DecisionAgent",
                action="declined",
                domain=domain,
                reason="No smells or run id.",
            )
            event_bus.emit(
                "facts.emit",{
                    "stage":"decision",
                    "component":"DecisionAgent",
                    "result":"declined",
                    "reason":"missing_run_id_or_smells",
                    "smell details":{"smells":smells},
                    "run id details":{"run_id":run_id},
                }
            )

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
            event_bus.emit(
                    "facts.emit",{
                        "stage":"decision",
                        "component":"DecisionAgent",
                        "result":"accepted",
                        "reason":"Low confidence",
                        "confidence":confidence,
                    }
                )

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
        event_bus.emit(
                    "facts.emit",{
                        "stage":"decision",
                        "component":"DecisionAgent",
                        "result":"stored",
                        "reason":"decision stored",
                        "decision":decision,
                    }
                )
        
        if raw is None:
            run_context.touch(
                run_id,
                agent="DecisionAgent",
                action="Returned none",
                domain=domain,
                reason="No raw payload",
            )
            event_bus.emit(
                    "facts.emit",{
                        "stage":"decision",
                        "component":"DecisionAgent",
                        "result":"accepted",
                        "reason":"no_raw_payload_no_intent",
                    }
                )

        run_context.touch(
                run_id,
                agent="DecisionAgent",
                action="organized",
                domain=domain,
                reason="Processed",
                confidence=confidence,
            )
            
        event_bus.emit(
                    f"intent.organize.{domain}",{
                    "domain":domain,
                    "confidence":confidence,
                    "run_id":run_id,
                    "raw":raw,
                    "source":source,
                    
                    }
                )
    
    @log_action(action="agt-updating-confidence")
    @on_event("confidence.updated")
    def update_confidence(self, payload):
        key = (payload["smell"], payload["intent"])
        self.confidence[key] = payload["trust"]

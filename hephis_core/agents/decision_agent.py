from hephis_core.environment import ENV
from hephis_core.events.decorators import on_event
from hephis_core.utils.logger_decorator import log_action
from hephis_core.swarm.decisions import store_decision
from hephis_core.events.bus import event_bus

class DecisionAgent:

    THRESHOLD = 0.4
    def __init__(self):
        print("INIT:",self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @log_action(action="agt-deciding-by-smell")
    @on_event("system.smells.post.extraction")
    def decide(self, payload):

        print("DECISION AGENT RECEIVED:", payload)

        smells = payload.get("smells",{})
        source = payload.get("source")
        run_id = payload.get("run_id")
        raw = payload.get("raw")

        if not run_id or not smells:
            return

        candidates = {
            domain: score
            for domain, score in smells.items()
            if score >= self.THRESHOLD
        }

        if not candidates:
            event_bus.emit(
                "intent.defer",
                {
                    "source":source,
                    "run_id":run_id,
                    "confidence":smells
                }
            )
            return

        weighted = {}

        for domain, score in candidates.items():
            smell = domain
            intent = f"organize.{domain}"
            trust = self.confidence.get((smell,intent),1.0)
            
            if trust < self.THRESHOLD:
                continue
            
        chosen_domain, confidence = max (
            weighted.items(),
            key=lambda item:item[1]
            )
        
        decision = {
            "domain": chosen_domain,
            "confidence": confidence,
            "smells": smells,
            "source": source,
            "run_id": run_id,
        }

        store_decision(run_id, decision)

        if raw is None:
            return
        
        event_bus.emit(
            f"intent.organize.{chosen_domain}",
            {
                "domain": chosen_domain,
                "run_id": run_id,
                "confidence": confidence,
                "raw": raw,
                "source": source,
            }
        )
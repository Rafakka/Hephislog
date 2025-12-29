from hephis_core.environment import ENV
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.agents.confidence_agent import get_trust
from hephis_core.utils.logger_decorator import log_action
from hephis_core.swarm.decisions import store_decision

class DecisionAgent:

    THRESHOLD = 0.4

    @on_event("system.smells_updated")
    @on_event("system.smells.post.extraction")
    @log_action(action="agt-deciding-by-smell")
    def decide(payload):

        smells = payload.get("smells",{})
        source = payload.get("source")
        run_id = payload.get("run_id")
        raw = payload.get("raw")

        if not run_id or not smells:
            return

        candidates = {
            domain: score
            for domain, score in smells.items()
            if score >= THRESHOLD
        }

        if not candidates:
            event_bus.emit(
                "intend.defer",
                {
                    "source":source,
                    "run_id":run_id,
                    "confidence":smells
                }
            )
            return

        weighted = {}

        for domain, score in candidates.items():
            intent = f"organize.{domain}"
            trust = get_trust(domain, intent)
            weighted[domain] = score * trust
            
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

        if raw is None:
            return

        store_decision(run_id, decision)
        
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
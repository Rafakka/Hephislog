from hephis_core.environment import ENV
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.agents.confidence_agent import ConfidenceAgent
from hephis_core.utils.logger_decorator import log_action
from hephis_core.swarm.decisions import store_decision

CONFIDENCE = ConfidenceAgent()

class DecisionAgent:

    THRESHOLD = 0.4

    @on_event("system.smells_updated")
    @on_event("system.smells.post.extraction")
    @log_action(action="agt-deciding-by-smell")
    def decide(self,payload):

        smells = payload.get("smells",{})
        source = payload.get("source")
        run_id = payload.get("run_id")
        raw = payload.get("raw")
        domain = payload.get("domain")

        candidates = {
            domain:score
            for domain, score in smells.items()
            if score >= self.THRESHOLD
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

        weighted_candidates = {}

        for domain, smell_score in candidates.items():
            intent = f"organize.{domain}"
            trust = CONFIDENCE.get_trust(domain, intent)

            final_score = smell_score*trust
            weighted_candidates[domain] = final_score
            
        domain, confidence = max (
            weighted_candidates.items(),
            key=lambda item:item[1]
            )
        
        decision = {
            "domain": domain,
            "confidence": confidence,
            "smells": smells,
            "source": source,
            "run_id": run_id,
        }

        store_decision(run_id, decision)

        event_bus.emit (
            f"intent.organize.{domain}",
            {
            "raw":raw,
            "domain":domain,
            "source":source,
            "run_id":run_id,
            "intent":f"organize.{domain}",
            "confidence":confidence,
            "smells":smells,
            }
        )
from hephis_core.environment import ENV
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import EventBus
from hephis_core.agents.confidence_agent import ConfidenceAgent

CONFIDENCE = ConfidenceAgent()

class DecisionAgent:

    THRESHOLD = 0.7

    @on_event("system.smells.post.extraction")
    def decide(self,payload):

        smells = payload.get("smells",{})
        source = payload.get("source")
        run_id = payload.get("run_id")

        candidates = {
            domain:score
            for domain, score in smells.items()
            if score >= self.THRESHOLD
        }

        if not candidates:
            EventBus.emit(
                "intend.defer",
                {
                    "source":source,
                    "run_id":run_id,
                    "confidence":smells
                }
            )

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

        EventBus.emit (
            f"intent.organize.{domain}",
            {
            "source":source,
            "run_id":run_id,
            "intent":f"organize.{domain}",
            "confidence":confidence,
            "smells":smells,
            }
        )
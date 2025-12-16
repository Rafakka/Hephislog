from hephis_core.environment import ENV
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import EventBus

class DecisionAgent:

    THRESLHOLD = 0.7

    @on_event("system.smells.post.extraction")
    def decide(self,payload):

        smells = payload.get("smells",{})
        source = payload.get("source")
        run_id = payload.get("run_id")

        candidates = {
            domain:score
            for domain, score in smells.items()
            if score >= self.THRESLHOLD
        }

        if not candidates:
            EventBus.emit(
                "intend.defer",
                {
                    "soucer":source,
                    "run_id":run_id,
                    "confidence":smells
                }
            )
            return

            domain, confidence = max (candidates.items(), key=lambda item:item[1])

            EventBus.emit (
                f"intent.organize.{domain}",
                {
                "source":source,
                "run_id":run_id,
                "confidence":confidence,
                "smells":smells,
                }
            )
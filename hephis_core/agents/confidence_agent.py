from collections import defaultdict
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import EventBus
class ConfidenceAgent:

    def __init__(self):
        sel.trust = defaultdict(lambda:defaultdict(lambda:{"success":0,"failure":0}))
        sel.pending = {}

    @on_event("intent.*")
    def record_decisions(self, payload):
        run_id = payload.get("run_id")
        intent = payload.get("intent")
        smell = payload.get("smell")

        if not run_id or not intent or not smell:
            return
        
        self.pending[run_id] = {
            "smell":smell,
            "intend":intent,
        }

    @on_event("*.pipeline_finished")
    def learn_from_outcomes(self, payload):
        run_id = payload.get("run_id")
        domain = payload.get("domain")
        success = payload.get("success", True)

        if run_id not in self.pending:
            return
        
        decision = self.pending.pop(run_id)
        smell = decision["smell"]
        intent = decision["intent"]

        aligned = domain in intent

        if success and aligned:
            self.trust[smell][intent]["success"]+=1
        else:
            self.trust[smell][intent]["failure"]+=1
    
    def get_trust(self, smell:str, intent:str) -> float:
        stats = self.trust.get(smell,{}.get(intent))

        if not stats:
            return 1.0
        
        success = stats["success"]
        failure = stats["failure"]
        total = success + failure

        if total == 0:
            return 1.0
        
        return success / total
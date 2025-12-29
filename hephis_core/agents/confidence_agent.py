from collections import defaultdict
from hephis_core.events.decorators import on_event
from hephis_core.utils.logger_decorator import log_action

class ConfidenceMemory:
    def __init__(self):
        self.trust = defaultdict(lambda: defaultdict(lambda:{"success":0,"failure":0,}))
        self.pending = {}
    
CONFIDENCE = ConfidenceMemory()

@on_event("intent.*")
@log_action(action="agt-recording-decisions")
def record_decisions(payload):
    run_id = payload["run_id"]
    if not run_id:
        return
    CONFIDENCE.pending[run_id] = payload

@on_event("*.pipeline_finished")
@log_action(action="agt-learning-from-outcomes")
def learn_from_outcomes(payload):
    run_id = payload.get("run_id")
    domain = payload.get("domain")
    success = payload.get("success", True)

    decision = CONFIDENCE.pending.pop(run_id, None)

    if not decision:
        return
            
        smell = decision.get("smell")
        intent = decision.get("intent")

        if not smell or not intent:
            return
            
        stats = CONFIDENCE.trust[smell][intent]
        if success:
            stats["success"] +=1
        else:
            stats["failure"] +=1

    
def get_trust(smell:str, intent:str) -> float:
    stats = CONFIDENCE.trust.get(smell,{}.get(intent))

    if not stats:
        return 1.0
        
    total = stats["success"] + stats["failure"]
    if total == 0:
        return 1.0
        
    return stats["success"] / total
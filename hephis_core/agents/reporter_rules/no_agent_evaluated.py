from typing import Optional
from .base import reporter_rule, STAGE_GROUPS, RESULT_GROUPS, iter_facts

@reporter_rule
def rule_no_agent_evaluated(context: list[dict]) -> Optional[dict]:

   facts = iter_facts(context)
   
   agent_facts = [ 
    t for t in facts
    if t.get("stage") in STAGE_GROUPS["agent_activity"]
    ]
    
   if agent_facts:
        return None
    
   detector_facts = [
    t for t in facts
    if t.get("stage") in STAGE_GROUPS["detector_stages"] and t.get("result") in RESULT_GROUPS["decision_stages"]
    ]

   if not detector_facts:
    return None

    return {
            "type":"no_agents_evaluated",
            "message":"Signals were detected, but no agent evaluated the run",
            "detectors":sorted({
               f.get("component","unkown")
               for f in detector_facts
            }),
            "reason":"no_matching_agent"
        }
        
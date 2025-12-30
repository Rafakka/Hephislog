from typing import Dict, Any, Optional
from .base import reporter_rule

@reporter_rule
def rule_no_agent_evaluated(event:Dict[str,Any]) -> Optional[Dict[str, Any]]:
    facts = event.get("facts",[])

    agent_facts = [ 
        f for f in facts if f.stage == "agent"
    ]

    if agent_facts:
        return None
    
    detector_facts = [
        f for f in facts if f.stage == "detector" and f.result == "ok"
    ]

    if detector_facts:
        return {
            "type":"no_agents_evaluated",
            "message":"Signals were detected, but no agent evaluated the run",
            "detectors":[f.component for f in detector_facts],
            "reason":"no_matching_agent"
        }
        
    return None
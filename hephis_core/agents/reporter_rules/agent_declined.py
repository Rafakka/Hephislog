from typing import Dict, Any, Optional
from .base import reporter_rule, STAGE_GROUPS, RESULT_GROUPS

@reporter_rule
def rule_agent_declined(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:

    facts = context.get("facts",[])

    declined = [
        f for f in facts
        if f.get("stage") in STAGE_GROUPS["agent_activity"]
        and f.get("result") in RESULT_GROUPS["decision_failure"]
    ]

    if not declined:
        return None
    
    return {
        "type":"agent_declined",
        "message":"Agents evaluated the run but declined to act.",
        "agents":sorted({f.get("component","unkown")
        for f in declined}),
        "reason":"policy_decline",
        "details":[
            {
                "agent":f.get("component"),
                "stage":f.get("stage"),
                "reason":f.get("reason"),
            }
            for f in declined
        ]
    }
    
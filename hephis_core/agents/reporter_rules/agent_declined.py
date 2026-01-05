from typing import Dict, Any, Optional
from .base import reporter_rule

@reporter_rule
def rule_agent_declined(context):
    decisions = context.get("decisions",[])

    declined = [
        f for f in decisions.values()
        if f.get("result") == "declined"
    ]

    if not declined:
        return None
    
    return {
        "type":"agent_declined",
        "message":"Agents evaluated the run but declined to act.",
        "agents":[d.get("agent")for d in declined],
        "reason":"policy_decline"
    }
    
from typing import Dict, Any, Optional
from .base import reporter_rule

@reporter_rule
def rule_agent_declined(event:Dict[str, Any]) -> Optional[Dict[str, Any]]:
    facts = event.get("facts",[])

    declined_agents = [
        f for f in facts 
        if f.stage == "decision" and f.result == "declined"
    ]

    if not declined_agents:
        return None
    
    return {
        "type":"agent_declined",
        "message":"Agents evaluated the run but declined to act.",
        "agents":[f.component for f in declined_agents],
        "reason":"policy_decline"
    }
    
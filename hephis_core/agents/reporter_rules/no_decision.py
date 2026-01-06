from typing import Dict, Any, Optional
from .base import reporter_rule, STAGE_GROUPS, RESULT_GROUPS

@reporter_rule
def rule_no_decision(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:

    facts = context.get("facts",[])
    
    agent_activity = [
        t for t in facts
        if t.get("stage") in STAGE_GROUPS["agent_activity"]
    ]

    if not agent_activity:
        return None

    successful_decisions = [
        t for t in facts
        if t.get("stage") in STAGE_GROUPS["decision_stages"]
        and t.get("result") in RESULT_GROUPS["decision_success"]
    ]

    if successful_decisions:
        return None

    return {
            "type":"no_decision",
            "message":"Agent evaluted the run, but no decision was produced.",
            "agents":list({
               f.get("component","unkown")
               for f in agent_activity
            }),
            "reason":"No decision made",
        }


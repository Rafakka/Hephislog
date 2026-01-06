from typing import Dict, Any, Optional
from .base import reporter_rule, STAGE_GROUPS, RESULT_GROUPS

@reporter_rule
def rule_decision_not_consumed(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:

    facts = context.get("facts",[])

    decision_facts = [
        t for t in facts
        if t.get("stage") in STAGE_GROUPS["decision_stages"]
    ]

    if not decision_facts:
        return None
    
    decision_index = max(
        i for i, f in enumerate(facts)
        if f.get("stage") in STAGE_GROUPS["decision_stages"]
    )
    
    consumed = any(
        f.get("stage") in STAGE_GROUPS["agent_activity"]
        for f in facts[decision_index + 1:]
    )

    if consumed:
        return None

    last_decision = decision_facts[-1]
    
    return {
        "type":"decision_not_consumed",
        "message":"A decision was made, but no downstream agent acted on it.",
        "decision":{
            "component":last_decision.get("component"),
            "result":last_decision.get("result"),
            "reason":last_decision.get("reason"),
        },
        "reason":"no_consumer",
    }
from typing import Dict, Any, Optional
from .base import reporter_rule, RESULT_GROUPS, STAGE_GROUPS

@reporter_rule
def rule_explain_silence(event:Dict[str, Any]) -> Optional[Dict[str,Any]]:
    facts = event.get("facts",[])

    if not facts:
        return {
            "type":"silent_success",
            "reason":"no_facts_emitted",
            "message":"The pipeline completed without emitting any facts."
        }
    
    disruptive = [
        f for f in facts
        if (
            f.get("stage") in STAGE_GROUPS["decision_stages"]
            or f.get("stage") in STAGE_GROUPS["agent_activity"]
            or f.get("result") in RESULT_GROUPS["decision_failure"]
        )
    ]

    if disruptive:
        return None
    
    result_counts = {}

    for f in facts:
        r = f.get("result","unknown")
        result_counts[r] = result_counts.get(r,0) +1
    
    return {
        "type":"silent_success",
        "reason":"no_action_required",
        "message":"All agents completed successfully, but no actionable signal was produced.",
        "summary": {
            "total_facts":len(facts),
            "results":result_counts,
        },
    }
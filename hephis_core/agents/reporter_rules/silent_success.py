from typing import Dict, Any, Optional
from .base import reporter_rule

@reporter_rule
def rule_explain_silence(event:Dict[str, Any]) -> Optional[Dict[str,Any]]:
    facts = event.get("facts",[])

    if not facts:
        return {
            "type":"silent_success",
            "reason":"no_facts_emitted",
            "message":"The pipeline completed without emitting any facts."
        }
    
    if all(f.result in ("ok","none") for f in facts):
        return {
            "type":"silent_success",
            "reason":"no_action_required",
            "message":"All agents completed successfully, but no actionable signal was produced.",
            "summary":{
                "total_facts":len(facts),
                "ok":sum( 1 for f in facts if f.result == "ok"),
                "none":sum(1 for f in facts if f.result == "none"),
            }
        }
    return None

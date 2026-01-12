from typing import Optional
from .base import reporter_rule, STAGE_GROUPS, RESULT_GROUPS, run_completed, logger, iter_facts

@reporter_rule
def rule_agent_declined(context:list[dict]) -> Optional[dict]:

    facts = iter_facts(context)

    if run_completed(facts):
        logger.debug(
            "rule_agent_declined skippped: Run already completed"
        )
        return None

    declined = [
        f for f in facts
        if f.get("stage") in STAGE_GROUPS["agent_activity"]
        and f.get("result") in RESULT_GROUPS["decision_failure"]
    ]

    if not declined:
        logger.debug(
            "Rule_agent_declined skipped: no declined agent facts"
        )
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
    
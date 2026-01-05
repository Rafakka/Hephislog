from .base import reporter_rule

@reporter_rule
def rule_no_decision(context):
    timeline = context.get("timeline",[])
    
    agent_events = [
        t for t in timeline
        if t.get("stage") == "agent"
    ]

    if not agent_events:
        return None

    decision_events = [
        t for t in timeline
        if t.get("stage") == "decision"
    ]

    if not decision_events:
        return {
            "type":"no_decision",
            "message":"Agent evaluted the run, but no decision was produced.",
            "detectors":[t.get("agent") for t in agent_events],
            "reason":"No decision made",
        }
    return None


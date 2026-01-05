from .base import reporter_rule

@reporter_rule
def rule_decision_not_consumed(context):
    timeline = context.get("timeline",[])

    decision_events = [
        t for t in timeline
        if t.get("stage") == "decision"
    ]

    if not decision_events:
        return None
    
    consumed = any(
        t.get("stage") in ("organizer", "executor","packer", "finalizer")
        for t in timeline
    )

    if not consumed:
        return {
            "type":"decision not consumed",
            "message":"A decision was made bu7t no downstream agent acted on it",
            "decision":decision_events[-1].get("result"),
            "reason":"no_consumer",
        }
        
    return None
from .base import reporter_rule

@reporter_rule
def rule_no_agent_evaluated(context):
   timeline = context.get("timeline",[])
   
   agent_events = [ 
    t for t in timeline
    if t.get("stage") == "agent"
    ]
    
   if agent_events:
        return None
    
   detector_events = [
    t for t in timeline
    if t.get("stage") == "detector" and t.get("result") == "ok"
    ]

   if not detector_events:
    return None

    return {
            "type":"no_agents_evaluated",
            "message":"Signals were detected, but no agent evaluated the run",
            "detectors":[t.get("agent") for t in detector_events],
            "reason":"no_matching_agent"
        }
        
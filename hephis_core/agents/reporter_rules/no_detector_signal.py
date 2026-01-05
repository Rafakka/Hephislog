from .base import reporter_rule

@reporter_rule
def rule_no_detector_signal(context):
    timeline = context.get("timeline",[])

    detector_events = [
        f for f in timeline
        if f.get("stage") == "detector"
    ]

    if not detector_events:
        return None
    
    if all(t.get("result") in  ("none",None) for t in detector_events):
        return {
            "type":"no_detector_signal",
            "message":"All detectors completed without emitting a signal.",
            "detectors":[t.get("agent") for t in detector_events],
            "reason":"no_signal_detected"
        }

    return None
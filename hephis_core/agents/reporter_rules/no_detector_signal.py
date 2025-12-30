from typing import Dict, Any, Optional
from .base import reporter_rule

@reporter_rule
def rule_no_detector_signal(event:Dict[str, Any])->Optional[Dict[str, Any]]:
    facts = event.get("facts",[])

    detector_facts = [
        f for f in facts if f.stage == "detector"
    ]

    if not detector_facts:
        return None
    
    if all(f.result ==  "none" for f in detector_facts):
        return {
            "type":"no_detector_signal",
            "message":"All detectors completed without emitting a signal.",
            "detectors":[f.component for f in detector_facts],
            "reason":"no_signal_detected"
        }

    return None
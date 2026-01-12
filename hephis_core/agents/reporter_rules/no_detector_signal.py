from typing import Optional
from .base import reporter_rule, STAGE_GROUPS, RESULT_GROUPS, iter_facts

@reporter_rule
def rule_no_detector_signal(facts:list[dict]) -> Optional[dict]:

    detector_facts = [
        f for f in facts
        if f.get("stage") in STAGE_GROUPS["detector_stages"]
    ]

    if not detector_facts:
        return None
    
    if any(
        f.get("result") in RESULT_GROUPS["detector_positive"]
        for f  in detector_facts
    ):
        return none
    
    return {
        "type":"no_detector_signal",
        "message":"All detectors completed without emitting a signal",
        "detectors": sorted ({
            f.get("component","unkown")
            for f in detector_facts
        }),
        "reason":"no_signal_detected",
        "details":[
            {
                "detector":f.get("component"),
                "result":f.get("result"),
                "reason":f.get("reason"),
            }
            for f in detector_facts
        ],
    }
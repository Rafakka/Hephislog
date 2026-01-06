from typing import Dict, Any, Optional

STAGE_GROUPS = {
    "agent_activity" :{
        "decision",
        "organizer",
        "finalizer",
        "gatekeeper",
        "identifier",
    },
    "decision_stages": {
        "decision",
    },
    "detector_stages":{
        "sniffer",
        "confidence",
        "detector",
    },
}

RESULT_GROUPS = {
    "decision_success":{
        "stored",
        "accepted",
        "ok",
    },
    "decision_failure": {
        "declined",
        "ignored",
        "rejected",
    },
    "detector_no_signal": {
        "no_signal",
        "no_match",
        "empty",
    },
    "detector_positive": {
        "signal",
        "match",
        "triggered",
    }
}

ReportFinding = Dict[str, Any]
RunEvent = Dict[str, Any]

def reporter_rule(fn):
    fn._is_reporter_rule = True
    return fn

from typing import Dict, Any, Optional
import logging

logger=logging.getLogger("hephis.reporter")

STAGE_GROUPS = {
    "agent_activity" :{
        "decision",
        "organizer",
        "finalizer",
        "gatekeeper",
        "identifier",
        "cleaning"
    },
    "decision_stages": {
        "decision",
    },
    "detector_stages":{
        "sniffing",
        "confidence",
        "detector",
        "advising",
    },
}

RESULT_GROUPS = {
    "decision_success":{
        "stored",
        "accepted",
        "ok",
        "completed",
        "cleaned",
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

def iter_facts(input) -> list[dict]:

    if isinstance(input, list):
        return [f for f in input if isinstance(f, dict)]
    if isinstance(input, dict):
        facts = input.get("facts",[])
        if isinstance(facts, list):
            return [f for f in facts if isinstance(f, dict)]
    return []
    
def reporter_rule(fn):
    fn._is_reporter_rule = True
    return fn

def run_completed(facts: list[dict]) -> bool:
    return any(
        f.get("stage") == "run_completed"
        for f in facts
        if isinstance(f, dict)
    )

def should_run_diagnostics(facts: list [dict]) -> bool:
    for f in facts:
        if (
            isinstance(f,dict)
            and f.get("stage") == "run"
            and f.get("result") in ("completed","success")
        ):
            return False
    return True
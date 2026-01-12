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

def iter_facts(context):
    if isinstance(context, list):
        return context
    if isinstance(context, dict):
        return context.get("facts",[])
    return[]

def reporter_rule(fn):
    fn._is_reporter_rule = True
    return fn

def run_completed(facts: list[dict]) -> bool:
    for f in facts:
        if f.get("stage") == "run_completed":
            return True
    return False

def should_run_diagnostics(context: dict) -> bool:
    for f in context.get("facts",[]):
        if (
            isinstance(f,dict)
            and f.get("stage") == "run"
            and f.get("result") in ("completed","success")
        ):
            return False
    return True
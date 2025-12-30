from typing import Dict, Any, Optional

ReportFinding = Dict[str, Any]
RunEvent = Dict[str, Any]

def reporter_rule(fn):
    fn._is_reporter_rule = True
    return fn

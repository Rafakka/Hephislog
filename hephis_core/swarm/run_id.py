from typing import Optional

def extract_run_id(payload:dict) -> Optional[str]:

    if not isinstance(payload, dict):
        return None
    return payload.get("run_id") or payload.get("id")
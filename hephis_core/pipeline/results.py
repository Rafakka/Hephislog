from threading import Lock

_PIPELINE_RESULTS = {}
_LOCK = Lock()

def store_result(run_id: str, payload: dict):
    with _LOCK:
        _PIPELINE_RESULTS[run_id] = payload

def get_result(run_id: str):
    with _LOCK:
        return _PIPELINE_RESULTS.get(run_id)

def pop_result(run_id: str):
    with _LOCK:
        return _PIPELINE_RESULTS.pop(run_id, None)
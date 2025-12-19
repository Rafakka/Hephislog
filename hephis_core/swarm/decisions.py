
_DECISIONS = {}

def store_decision(run_id:str, decision:dict):
    _DECISIONS[run_id] = decision

def get_decision(run_id:str):
    return _DECISIONS.get(run_id)

def reset_decisions():
    _DECISIONS.clear()

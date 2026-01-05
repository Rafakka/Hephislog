
class DecisionStore:
    def __init__(self):
        self._decisions = {}
    
    def store(self, run_id:str, decision:dict):
        self._decisions[run_id]=decision
    
    def get(self, run_id:str):
        return self._decisions.get(run_id)
    
    def reset(self):
        self._decisions.clear()

decision_store = DecisionStore()
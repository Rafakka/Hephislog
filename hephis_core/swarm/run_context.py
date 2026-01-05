
class RunContextStore:
    def __init__(self):
        self._runs = {}

    def get(self, run_id):
        return self._runs.get(run_id,{})

    def touch(self, run_id, **entry):
        ctx = self._runs.setdefault(run_id,{})
        timeline = ctx.setdefault("timeline",[])
        timeline.append(entry)
    
    def update(self, run_id, **fields):
        ctx = self._runs.setdefault(run_id,{})
        ctx.update(fields)

    def reset(self):
        self._runs.clear()
    
run_context = RunContextStore()
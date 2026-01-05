
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
    
    def emit_fact(
        self,
        run_id: str,
        *,
        stage:str,
        component:str,
        result:str,
        reason: str | None = None,
        details: dict | None = None
    ):
        ctx =self._runs.setdefault(run_id, {})

        fact = {
            "stage": stage,
            "component":component,
            "result": result,
            "reason":reason,
            "details":details,
        }

        ctx.setdefault("facts",[]).append(fact)

run_context = RunContextStore()
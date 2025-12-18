
from hephis_core.events.decorators import on_event
from hephis_core.pipeline.results import store_result

class FinalizerAgent:

    @on_event("*.pipeline_finished")
    def finalize_pipeline(self, payload):
        run_id = payload.get("run_id")

        if not run_id:
            return 

        store_result(run_id, payload)

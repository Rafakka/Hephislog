
from hephis_core.events.decorators import on_event
from hephis_core.pipeline.results import store_result
from hephis_core.utils.logger_decorator import log_action

class FinalizerAgent:

    
    @on_event("*.pipeline_finished")
    @log_action(action="agt-finalizing-pipeline")
    def finalize_pipeline(self, payload):
        run_id = payload.get("run_id")

        if not run_id:
            return 

        store_result(run_id, payload)

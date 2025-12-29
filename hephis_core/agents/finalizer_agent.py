
from hephis_core.events.decorators import on_event
from hephis_core.pipeline.results import store_result
from hephis_core.utils.logger_decorator import log_action

class FinalizerAgent:

    def __init__(self):
        for att_name in dir(self):
            attr = getattr(self, att_name)
            if callable(attr) and hasattr(attr, "_event_name"):
                event_bus.subscribe(attr._event_name, attr)

    @log_action(action="agt-finalizing-pipeline")
    @on_event("*.pipeline_finished")
    def finalize_pipeline(self, payload):
        run_id = payload.get("run_id")

        if not run_id:
            return 

        store_result(run_id, payload)

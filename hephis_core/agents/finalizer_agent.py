
from hephis_core.events.decorators import on_event
from hephis_core.pipeline.results import store_result
from hephis_core.utils.logger_decorator import log_action

class FinalizerAgent:

    def __init__(self):
        print("INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @log_action(action="agt-finalizing-pipeline")
    @on_event("*.pipeline_finished")
    def finalize_pipeline(self, payload):
        run_id = payload.get("run_id")

        if not run_id:
            return 

        store_result(run_id, payload)

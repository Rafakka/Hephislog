
from hephis_core.events.decorators import on_event
from hephis_core.pipeline.results import store_result
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context

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
        print("FINALIZER AGENT HANDLER CALLED",payload)
        run_id = payload.get("run_id")
        raw = payload.get("raw")
        domain = payload.get("domain")
        confidence = payload.get("confidence")
        source = payload.get("source")
        

        if not run_id:
            run_context.touch(
                run_id,
                agent="FinalizerAgent",
                action="store_result_failed",
                reason="run_id_not_found",
            )
            run_context.emit_fact(
                run_id,
                stage="finalize",
                component="FinalizerAgent",
                result="declined",
                reason="run_id_not_found"
                )
            return 

        store_result(run_id, payload)

        run_context.touch(
                run_id,
                agent="FinalizerAgent",
                action="store_result",
                reason="flow_completed",
            )
        run_context.emit_fact(
            run_id,
            stage="finalize",
            component="FinalizerAgent",
            result="Completed",
            reason="flow_completed"
            )

        event_bus.emit(
                    "system.run.completed",{
                    "domain":domain,
                    "confidence":confidence,
                    "run_id":run_id,
                    "raw":raw,
                    "source":source,
                    
                    }
                )
        

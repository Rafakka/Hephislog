
from hephis_core.events.decorators import on_event
from hephis_core.pipeline.results import store_result
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class FinalizerAgent:

    def __init__(self):
        print("9 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("*.pipeline_finished")
    def finalize_pipeline(self, payload):
        print("FINALIZER AGENT HANDLER CALLED",payload)
        run_id = extract_run_id(payload)
        data = payload["data"]
        domain = payload.get("domain")
        confidence = payload.get("confidence")
        source = payload.get("source")

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"finalizing-flow",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
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
            result="ok",
            reason="flow_completed"
            )

        event_bus.emit(
                    "system.run.completed",{
                    "domain":domain,
                    "confidence":confidence,
                    "run_id":run_id,
                    "data":data,
                    "source":source,
                    }
                )
        

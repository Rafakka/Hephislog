
from hephis_core.events.event_bus import EventBus
from hephis_core.events.decorators import on_event

PIPELINE_RESULTS = {}

class FinalizerAgent:

    @on_event("*.pipeline_finished")
    def finalize_pipeline(self, payload):
        domain = payload.get("domain")
        packed = payload.get("packed")
        source = payload.get("source")
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")
        
        if not run_id:
            return
        
        final_result = {
            "success": True,
            "domain": domain,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
            "output": {
                "path": packed.get("path"),
                "title": packed.get("title"),
                "domain": packed.get("domain"),
            },
        }

        PIPELINE_RESULTS[run_id] = final_result

        EventBus.emit(
            "pipeline.finalized",
            {
                "run_id": run_id,
                "domain": domain,
            }
        )
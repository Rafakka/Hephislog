from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class UniversalPackerAgent:

    def __init__(self):
        print("8 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
                
    @on_event("music.normalized")
    def handle_music(self, payload):
        print("PACKER MUSIC HANDLER CALLED",payload)
        self._pack_domain("music", payload)

    @on_event("recipe.normalized")
    def handle_recipe(self, payload):
        print("PACKER RECIPE HANDLER CALLED",payload)
        self._pack_domain("recipe", payload)

    def _pack_domain(self, domain: str, payload: dict):
        print("RAN:",self.__class__.__name__) 
        normalized = payload["normalized"]
        source = payload.get("source")
        run_id = extract_run_id(payload)
        confidence = payload.get("confidence")

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"universal-packer",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        if isinstance(normalized, dict) and "data" in normalized:
            normalized_content = normalized["data"]
        else:
            normalized_content = normalized

        if hasattr(normalized_content, "model_dump"):
            serialized = normalized_content.model_dump()
        else:
            serialized = normalized_content

        packed = pack_data(domain, normalized_content)

        if not packed:
            run_context.touch(
                run_id,
                agent="UniversalPackerAgent",
                action="declined_file",
                domain=domain,
                reason="file_not_packed",
            )
            run_context.emit_fact(
                run_id,
                stage="packer",
                component="UniversalPackerAgent",
                result="declined",
                reason="file_not_packed",
                )
            return

        run_context.touch(
                run_id,
                agent="UniversalPackerAgent",
                action="packing_file",
                domain=domain,
                reason="valid_file_type",
            )
        run_context.emit_fact(
                run_id,
                stage="packing",
                component="UniversalPackerAgent",
                result="ok",
                reason="valid_file_type",
                )

        event_bus.emit(
            f"{domain}.pipeline_finished",
            {
                "normalized": serialized,
                "data": packed,
                "source": source,
                "domain":domain,
                "confidence": confidence,
                "run_id": run_id,
            }
        )
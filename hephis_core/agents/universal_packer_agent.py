from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context

class UniversalPackerAgent:

    def __init__(self):
        print("INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
    
                
    @log_action(action="agt-packing-music")
    @on_event("music.normalized")
    def handle_music(self, payload):
        print("PACKER MUSIC HANDLER CALLED",payload)
        self._pack_domain("music", payload)

    @log_action(action="agt-packing-recipe")
    @on_event("recipe.normalized")
    def handle_recipe(self, payload):
        print("PACKER RECIPE HANDLER CALLED",payload)
        self._pack_domain("recipe", payload)

    def _pack_domain(self, domain: str, payload: dict):

        normalized = payload["normalized"]
        source = payload["source"]
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")

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
                stage="universalpackeragent",
                component="UniversalPackerAgent",
                result="declined",
                reason="file_not_packed",
                )
            return

        run_context.touch(
                run_id,
                agent="UniversalPackerAgent",
                action="packed_file",
                domain=domain,
                reason="valid_file_type",
            )
        run_context.emit_fact(
                run_id,
                stage="universalpackeragent",
                component="UniversalPackerAgent",
                result="packed_file",
                reason="valid_file_type",
                )

        event_bus.emit(
            f"{domain}.pipeline_finished",
            {
                "normalized": serialized,
                "packed": packed,
                "source": source,
                "confidence": confidence,
                "run_id": run_id,
            }
        )
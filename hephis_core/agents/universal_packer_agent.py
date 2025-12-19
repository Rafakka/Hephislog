from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.event_bus import event_bus
from hephis_core.events.decorators import on_event

class UniversalPackerAgent:

    @on_event("music.normalized")
    @log_action(action="agt-packing-music")
    def handle_music(self, payload):
        self._pack_domain("music", payload)

    @on_event("recipe.normalized")
    @log_action(action="agt-packing-recipe")
    def handle_recipe(self, payload):
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
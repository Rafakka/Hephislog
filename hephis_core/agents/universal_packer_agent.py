from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.events.event_bus import event_bus
from hephis_core.events.decorators import on_event

class UniversalPackerAgent:

    @on_event("music.normalized")
    def handle_music(self, payload):
        self._pack_domain("music", payload)

    @on_event("recipe.normalized")
    def handle_recipe(self, payload):
        self._pack_domain("recipe", payload)

    def _pack_domain(self, domain: str, payload: dict):

        normalized = payload["normalized"]
        source = payload["source"]

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
                "source": source,
                "normalized": serialized,
                "packed": packed
            }
        )
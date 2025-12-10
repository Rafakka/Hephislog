from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer

class UniversalPackerAgent:

    @on_event("universal.normalized")
    def pack(self, payload, event_name=None):
        pass

    @on_event("music.normalized")
    def handle_music(self, payload):
        self._pack_domain("music", payload)

    @on_event("recipe.normalized")
    def handle_recipe(self, payload):
        self._pack_domain("recipe",payload)

    def _pack_domain(self, domain:str, payload:dict):

        normalized = payload["normalized"]
        url = payload["url"]

        packed = pack_data(domain, normalized)

        announcer.emit("{domain}.pipeline_finished", {
            "url": url,
            "normalized": normalized.model_dump(),
            "packed": packed
        })
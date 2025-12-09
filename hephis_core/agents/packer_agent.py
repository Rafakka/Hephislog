from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer

class PackerAgent:

    @on_event("music.normalized")
    def music_packer(self, payload):
        
        normalized = payload["normalized"]
        url = payload["url"]

        packed = pack_data("music", normalized)

        announcer.emit("music.pipeline_finished", {
            "url": url,
            "normalized": normalized.model_dump(),
            "packed": packed
        })

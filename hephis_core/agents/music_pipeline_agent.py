from hephis_core.modules.music_normalizer.normalizer import music_normalizer
from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer


class MusicPipelineAgent:

    @on_event("music.organized")
    def normalize_music(self, payload):
        
        sections = payload["sections"]
        url = payload["url"]

        normalized = music_normalizer(
            raw_lines=sections,
            url=url,
            run_id="pipeline-agent"
        )

        announcer.emit("music.normalized", {
            "normalized": normalized,
            "url": url
        })
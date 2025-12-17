from hephis_core.modules.music_normalizer.normalizer import music_normalizer
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.events.event_bus import EventBus
from hephis_core.events.decorators import on_event

class NormalizerAgent:

    @on_event("music.organized")
    def normalize_music(self, payload):

        sections = payload["sections"]
        source = payload["source"]
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")

        normalized = music_normalizer(
            raw_lines=sections,
            url=source,
            run_id=run_id or "pipeline-agent"
        )

        EventBus.emit("music.normalized", {
            "domain": "music",
            "normalized": normalized,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })

    @on_event("recipe.organized")
    def normalize_recipe(self, payload):

        sections = payload["sections"]
        source = payload["source"]
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")

        normalized = recipe_normalizer(
        recipe,
        schema_version="1.0",
        module_version="1.0"
        )

    EventBus.emit("recipe.normalized", {
        "domain": "recipe",
        "normalized": normalized,
        "source": source,
        "confidence": confidence,
        "run_id": run_id,
    })
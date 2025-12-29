from hephis_core.modules.music_normalizer.normalizer import music_normalizer
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.events.event_bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.utils.logger_decorator import log_action

class NormalizerAgent:

    def __init__(self):
        for att_name in dir(self):
            attr = getattr(self, att_name)
            if callable(attr) and hasattr(attr, "_event_name"):
                event_bus.subscribe(attr._event_name, attr)


    @log_action(action="agt-normalizing-music")
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

        event_bus.emit("music.normalized", {
            "domain": "music",
            "normalized": normalized,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })

    @log_action(action="agt-normalizing-recipe")
    @on_event("recipe.organized")
    def normalize_recipe(self, payload):

        raw = payload["sections"]
        source = payload["source"]
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")

        normalized = recipe_normalizer(
        raw,
        schema_version="1.0",
        module_version="1.0"
        )

        event_bus.emit("recipe.normalized", {
            "domain": "recipe",
            "normalized": normalized,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
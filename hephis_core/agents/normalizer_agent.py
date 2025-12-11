from hephis_core.modules.music_normalizer.normalizer import music_normalizer
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.events.event_bus import event_bus
from hephis_core.events.decorators import on_event

class NormalizerAgent:

    @on_event("music.organized")
    def normalize_music(self, payload):
        
        sections = payload["sections"]
        source = payload["source"]

        normalized = music_normalizer(
            raw_lines=sections,
            url=source,
            run_id="pipeline-agent"
        )

        event_bus.emit("music.normalized", {
            "normalized": normalized,
            "source": source
        })
    
    @on_event("recipe.organized")
    def normalize_recipe(self, payload):

        recipe = payload["recipe"]
        source = payload["source"]

        normalized = recipe_normalizer(
            recipe=recipe,
            schema_version="1.0",
            module_version="1.0"
        )

        event_bus.emit("recipe.normalized", {
            "normalized": normalized,
            "source": source
        })

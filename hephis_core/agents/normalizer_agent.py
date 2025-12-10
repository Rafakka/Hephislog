from hephis_core.modules.music_normalizer.normalizer import music_normalizer
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer


class NormalizerAgent:

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
    
    @on_event("recipe.organized")
    def normalize_recipe(self, payload):

        recipe = payload["recipe"]
        url = payload["url"]

        normalized = recipe_normalizer(
            recipe=recipe,
            url=url,
            run_id="pipeline-agent"
        )
        announcer.emit("recipe.normalized", {
            "normalized": normalized,
            "url": url
        })
    
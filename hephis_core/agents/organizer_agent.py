from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus
from hephis_core.utils.logger_decorator import log_action

class OrganizerAgent:

    @on_event("intent.organize.music")
    @log_action(action="agt-organizing-music")
    def handle_music(self, payload):
        raw = payload["raw"]
        source = payload.get("source")
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")

        paragraphs = raw.get("paragraphs", [])

        sections = music_organizer(paragraphs)

        event_bus.emit("music.organized", {
            "domain": "music",
            "sections": sections,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
    
    @on_event("intent.organize.recipe")
    @log_action(action="agt-organizing-recipe")
    def handle_recipe(self, payload):
        raw = payload["raw"]
        source = payload["source"]
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")

        event_bus.emit("recipe.organized", {
            "domain": "recipe",
            "recipe": raw,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })

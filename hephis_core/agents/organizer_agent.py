
from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus

from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus

class OrganizerAgent:

    @on_event("music.raw_extracted")
    def handle_music_raw(self, payload):

        raw = payload["raw"]
        source = payload["source"]

        paragraphs = raw.get("paragraphs", [])
        sections = music_organizer(paragraphs)

        event_bus.emit("music.organized", {
            "sections": sections,
            "source": source,
            "run_id": "organizer-agent"
        })
    
    @on_event("recipe.raw_extracted")
    def handle_recipe(self, payload):

        raw = payload["raw"]
        source = payload["source"]

        recipe = raw

        event_bus.emit("recipe.organized", {
            "recipe": recipe,
            "source": source,
            "run_id": "organizer-agent"
        })
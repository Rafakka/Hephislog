
from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer

class OrganizerAgent:

    @on_event("music.raw_extracted")
    def handle_music_raw(self, payload):

        raw = payload["raw"]
        url = payload["url"]

        paragraphs = raw.get("paragraphs", [])
        sections = music_organizer(paragraphs)

        # Emit organized data
        announcer.emit("music.organized", {
            "sections": sections,
            "url": url
        })
    
    @on_event("recipe.raw_extracted")
    def handle_recipe(self, payload):

        raw = payload["raw"]
        url = payload["url"]

        recipe = raw

        announcer.emit("recipe.organized", {
            "recipe": recipe,
            "url": url
        })
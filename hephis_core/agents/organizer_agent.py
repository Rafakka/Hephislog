from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class OrganizerAgent:

    def __init__(self):
        print("6 - INIT:", self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("intent.organize.music")
    def handle_music(self, payload):
        print("ORGANIZER MUSIC HANDLER CALLED",payload)

        raw = payload["raw"]
        source = payload.get("source")
        run_id = extract_run_id(payload)
        confidence = payload.get("confidence")

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"organizing-music",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return
        
        paragraphs = raw.get("lyrics",[])

        if not paragraphs:
            paragraphs = [raw.get("text","")]

        sections = music_organizer(paragraphs)

        if not sections:
            run_context.touch(
                run_id,
                agent="OrganizerAgent",
                action="declined",
                domain="music",
                reason="No sections",
            )
            run_context.emit_fact(
                run_id,
                stage="decision",
                component="OrganizerAgent",
                result="declined",
                reason="No sections",
                )
            return

        run_context.touch(
                run_id,
                agent="OrganizerAgent",
                action="organized",
                domain="music",
                reason="file_accepted",
            )
        run_context.emit_fact(
            run_id,
            stage="decision",
            component="OrganizerAgentt",
            result="accepted",
            reason="file_accepted"
            )

        event_bus.emit("music.organized", {
            "domain": "music",
            "sections": sections,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
        
    @on_event("intent.organize.recipe")
    def handle_recipe(self, payload):
        
        raw = payload["raw"]
        source = payload.get("source")
        run_id = extract_run_id(payload)
        confidence = payload.get("confidence")

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"organizing-recipe",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        if not raw:
            run_context.touch(
                run_id,
                agent="OrganizerAgent",
                action="declined",
                domain="Recipe",
                reason="No raw",
            )
            run_context.emit_fact(
                run_id,
                stage="decision",
                component="OrganizerAgent",
                result="declined",
                reason="No raw",
                )
            return

        run_context.touch(
            run_id,
            agent="OrganizerAgent",
            action="organized",
            domain="recipe",
            reason="file_accepted",
            )

        run_context.emit_fact(
            run_id,
            stage="decision",
            component="OrganizerAgent",
            result="accepted",
            reason="file_accepted"
            )

        event_bus.emit("recipe.organized", {
            "domain": "recipe",
            "recipe": raw,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
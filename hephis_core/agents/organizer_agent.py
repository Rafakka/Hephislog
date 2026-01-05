from hephis_core.services.cleaners.chord_cleaner import music_organizer
from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.utils.logger_decorator import log_action
from hephis_core.swarm.run_context import run_context

class OrganizerAgent:

    def __init__(self):
        print("INIT:", self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @log_action(action="agt-organizing-music")
    @on_event("intent.organize.music")
    def handle_music(self, payload):
        print("ORGANIZER MUSIC HANDLER CALLED",payload)

        raw = payload["raw"]
        source = payload.get("source")
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")
        
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
                stage="decisionagent",
                component="DecisionAgent",
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
            stage="decisionagent",
            component="DecisionAgent",
            result="organized",
            reason="file_accepted"
            )

        event_bus.emit("music.organized", {
            "domain": "music",
            "sections": sections,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
        
    @log_action(action="agt-organizing-recipe")
    @on_event("intent.organize.recipe")
    def handle_recipe(self, payload):
        
        raw = payload["raw"]
        source = payload["source"]
        run_id = payload.get("run_id")
        confidence = payload.get("confidence")

        if not run_id or not raw:
            run_context.touch(
                run_id,
                agent="OrganizerAgent",
                action="declined",
                domain="Recipe",
                reason="No run_id or no raw",
            )
            run_context.emit_fact(
                run_id,
                stage="decisionagent",
                component="DecisionAgent",
                result="declined",
                reason="No run_id or no raw",
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
            stage="decisionagent",
            component="DecisionAgent",
            result="organized",
            reason="file_accepted"
            )

        event_bus.emit("recipe.organized", {
            "domain": "recipe",
            "recipe": raw,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
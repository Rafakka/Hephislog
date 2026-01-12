from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from bs4 import Tag
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
    
    def organize_lines(self, text:str) -> list[dict]:

        lines = [l.rstrip() for l in text.splitlines()]

        blocks = []
        current = {"lyrics":None, "chords":None}

        for line in lines:
            if not line.strip():
                continue
            
            if ChordDetector.looks_like_chord_line(line):
                if current["chords"] is not None:
                    blocks.append(current)
                    current = {"lyrics":None,"chords":None}

                current["chords"] = line
            else:

                if current["lyrics"] is not None:
                    blocks.append(current)
                    current = {"lyrics":None,"chords":None}
                current["lyrics"] = line
        
            if current["lyrics"] or current["chords"]:
                blocks.append(current)

            return blocks

    @on_event("intent.organize.music")
    def handle_music(self, payload):
        print("RAN:",self.__class__.__name__) 
        raw = payload.get("raw",{})
        text = raw.get("text","")
        source = payload.get("source")
        run_id = extract_run_id(payload)
        confidence = payload.get("confidence")

        if not raw:
            run_context.touch(
                run_id,
                agent="OrganizerAgent",
                action="declined",
                domain="music",
                reason="No raw",
            )
            run_context.emit_fact(
                run_id,
                stage="organizer",
                component="OrganizerAgent",
                result="declined",
                reason="No raw",
                )
            return

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
        
        if not isinstance(text, str) or not text.strip():
            logger.warning("Organizer agent received empty or invalid text",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"organizing-music",
                    "run_id":run_id,
                }
            )
            return
        
        blocks = self.organize_lines(text)

        if not blocks:
            run_context.touch(
                run_id,
                agent="OrganizerAgent",
                action="declined",
                domain="music",
                reason="No blocks created",
            )
            run_context.emit_fact(
                run_id,
                stage="organizer",
                component="OrganizerAgent",
                result="declined",
                reason="No blocks created",
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
            stage="organizer",
            component="OrganizerAgent",
            result="accepted",
            reason="file_accepted"
            )

        print(f"THIS IS SECTIONS ORGANIZED: {blocks}")

        event_bus.emit("music.organized", {
            "domain": "music",
            "sections": blocks,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
        
    @on_event("intent.organize.recipe")
    def handle_recipe(self, payload):
        
        raw = payload.get("raw")

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
                stage="organizer",
                component="OrganizerAgent",
                result="declined",
                reason="No raw",
                )
            return

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

        run_context.touch(
            run_id,
            agent="OrganizerAgent",
            action="organized",
            domain="recipe",
            reason="file_accepted",
            )

        run_context.emit_fact(
            run_id,
            stage="organizer",
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
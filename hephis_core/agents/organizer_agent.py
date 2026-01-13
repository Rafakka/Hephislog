from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.cleaners.chord_cleaner import normalize_chord_line
from hephis_core.schemas.music_schemas import ChordSheetSchema, ChordLineSchema, ChordSectionSchema
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
        
        pending_chords: list[str] | None = None

        for line in lines:
            if not line.strip():
                continue

            if ChordDetector.looks_like_chord_line(line):
                pending_chords = normalize_chord_line(line).split()
                continue

            blocks.append({
                "lyrics":line,
                "chords":pending_chords or [],
            })

        return blocks

    @on_event("intent.organize.music")
    def handle_music(self, payload):
        print("RAN:",self.__class__.__name__)

        raw = payload.get("raw",{})
        text = raw.get("text","")
        source = payload.get("source")
        run_id = extract_run_id(payload)
        confidence = payload.get("confidence")

        title = payload.get("title") or "Unknown title"
        instrument=payload.get("instrument") or "Unknown instrument"
        key=payload.get("key") or "Unknown key"
        url=payload.get("url") or source

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
        
        print(f"THIS IS TEXT BEFORE ORGANIZED: {text}")

        lines = self.organize_lines(text)

        if not lines:
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
        
        section = ChordSectionSchema(
            name = title,
            lines = [
                ChordLineSchema(**line)
                if isinstance(line, dict)
                else line
                for line in lines
            ]
        )

        sections = [section]
        
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

        assert sections is not None, "Section is none before schema creation"
        assert isinstance(sections, list), type(sections)

        sheet = ChordSheetSchema (
            title = title,
            instrument= instrument,
            key=key,
            sections=sections,
            source=source,
            url=url,
            run_id=run_id
        )

        print(f"FINAL SHEET:", sheet.model_dump())

        event_bus.emit("music.organized", {
            "domain": "music",
            "sheet":sheet.model_dump(),
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
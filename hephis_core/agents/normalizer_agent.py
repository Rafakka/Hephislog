from hephis_core.modules.music_normalizer.normalizer import music_normalizer
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class NormalizerAgent:

    def __init__(self):
        print("7 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("music.organized")
    def normalize_music(self, payload):
        print("NORMALIZER MUSIC HANDLER CALLED",payload)

        sections = payload["sections"]
        source = payload.get("source")
        run_id = extract_run_id(payload)
        confidence = payload.get("confidence")

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"normalizing-music",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        normalized = music_normalizer(
            raw_lines=sections,
            url=source,
            run_id=run_id or "pipeline-agent"
        )

        if not normalized:
            run_context.touch(
                run_id,
                agent="NormalizerAgent",
                action="declined",
                domain="music",
                reason="Failed at normalizing",
            )
            run_context.emit_fact(
                run_id,
                stage="normalized",
                component="NormalizerAgent",
                result="declined",
                reason="failed at normalizing",
                )

        run_context.touch(
                run_id,
                agent="NormalizedAgent",
                action="normalized",
                domain="music",
                reason="File normalized",
            )
        run_context.emit_fact(
                run_id,
                stage="normalized",
                component="NormalizedAgent",
                result="accepted",
                reason="File Normalized",
                )


        event_bus.emit("music.normalized", {
            "domain": "music",
            "normalized": normalized,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })

    @on_event("recipe.organized")
    def normalize_recipe(self, payload):

        raw = payload["sections"]
        source = payload.get("source")
        run_id = extract_run_id(payload)
        confidence = payload.get("confidence")

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"normalizing-recipe",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        normalized = recipe_normalizer(
        raw,
        schema_version="1.0",
        module_version="1.0"
        )

        if not normalized:
            run_context.touch(
                run_id,
                agent="NormalizerAgent",
                action="declined",
                domain="recipe",
                reason="Failed at normalizing",
            )
            run_context.emit_fact(
                run_id,
                stage="normalized",
                component="NormalizerAgent",
                result="declined",
                reason="failed at normalizing",
                )

        run_context.touch(
                run_id,
                agent="NormalizerAgent",
                action="normalized",
                domain="recipe",
                reason="File normalized",
            )
        run_context.emit_fact(
                run_id,
                stage="normalized",
                component="NormalizerAgent",
                result="accepted",
                reason="File Normalized",
                )

        event_bus.emit("recipe.normalized", {
            "domain": "recipe",
            "normalized": normalized,
            "source": source,
            "confidence": confidence,
            "run_id": run_id,
        })
from hephis_core.modules.music_normalizer.normalizer import music_normalizer
from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
from hephis_core.modules.recipe_evaluator.evaluator import evaluate_recipe
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
        print("RAN:",self.__class__.__name__)
        sheet = payload.get("sheet")

        if not sheet:
            logger.warning("Normalizer received event without sheet.")
            return
        
        if hasattr(sheet,"model_dump"):
            sheet = sheet.model_dump()    

        run_id = sheet["run_id"]

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

        raw_lines = [
            line
            for section in sheet["sections"]
            for line in section["lines"]
        ]

        normalized = music_normalizer(
            raw_lines=raw_lines,
            url=sheet["source"],
            run_id=sheet["run_id"]
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
            return

        sheet["normalized"] = normalized

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
            "domain":"music",
            "sheet":sheet,
            "confidence":payload.get("confidence"),
            "run_id": run_id
        })

    @on_event("recipe.softly_paged")
    def normalize_recipe(self, payload):
        print("RAN:",self.__class__.__name__)

        print("THIS IS FULL PAYLOAD: ", payload)

        run_id = payload.get("run_id")

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

        recipe_page = payload.get("recipe")

        if not recipe_page:
            logger.warning("Normalizer received no recipe",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"normalizing-recipe",
                }
            )
            return

        confidence = payload.get("confidence")

        if not confidence:
            logger.warning("Normalizer received no confidence to save.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"normalizing-recipe",
                }
            )
            return
        
        raw_recipe = {
            "title":recipe_page.get("title"),
            "steps":recipe_page.get("steps"),
            "ingredients":recipe_page.get("ingredients"),
            "spices":recipe_page.get("structured",{}.get("spices",[])),
            "source":recipe_page.get("source"),
        }

        print("THIS IS RAW RECIPE: ",raw_recipe)

        normalized = recipe_normalizer(
        raw_recipe,
        schema_version="1.0",
        module_version="1.0"
        )

        print("THIS IS NORMALIZED DATA: ",normalized["data"])

        if not normalized or not normalized.get("success"):
            logger.warning("Normalizer not worked.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"normalizing-recipe",
                }
            )
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
            return
        
        data = normalized.get("data")
        if not isinstance(data, dict):
            logger.warning("Normalized data not structured.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"normalizing-recipe",
                }
            )
            run_context.touch(
                run_id,
                agent="NormalizerAgent",
                action="declined",
                domain="recipe",
                reason="Failed at structuring",
            )
            run_context.emit_fact(
                run_id,
                stage="normalized",
                component="NormalizerAgent",
                result="declined",
                reason="failed at normalizing",
                )
            return

        scores = evaluate_recipe(raw_recipe, data)

        if not scores:
            logger.warning("Evaluation error.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"evaluating-recipe",
                }
            )
            run_context.touch(
                run_id,
                agent="NormalizerAgent",
                action="declined",
                domain="recipe",
                reason="Failed at evaluating",
            )
            run_context.emit_fact(
                run_id,
                stage="evaluation",
                component="NormalizerAgent",
                result="declined",
                reason="failed at evaluating",
                )
            return

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

        event_bus.emit("recipe.normalized", 
            {
            "domain":"recipe",
            "normalized":normalized["data"],
            "metadata":normalized["data"].get("_metadata"),
            "source":raw_recipe.get("source"),
            "scores":scores,
            "confidence":confidence,
            "run_id": run_id,
            }
        )
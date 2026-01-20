from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.schemas.recipe_schemas import build_recipe_page
import logging

logger = logging.getLogger(__name__)

class RecipeWriterAgent:
    def __init__(self):
        print("* - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("recipe.organized.to.writer")
    def recipe_writer(self, payload):
        print("RAN:",self.__class__.__name__)

        print("THIS IS PAYLOAD: ",payload)

        run_id = extract_run_id(payload)
    
        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"recipe-writer",
                }
            )
            return
        
        recipe = payload.get("recipe")

        if not recipe:
            logger.warning("Writer received recipe without data.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"recipe-writer",
                }
            )
            return

        confidence = payload.get("confidence")

        if not confidence:
            logger.warning("Writer received no confidence to save.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"recipe-writer",
                }
            )
            return

        source = payload.get("source")

        if not confidence:
            logger.warning("Writer received no source from data.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"recipe-writer",
                }
            )
            return
        
        recipe_page =  build_recipe_page(raw_recipe=recipe,run_id=run_id,confidence=confidence,source=source)

        if recipe_page == None:
            run_context.touch(
                run_id,
                agent="RecipeWriter",
                action="declined",
                domain="recipe",
                reason="Failed at -page-ing- recipe",
            )
            run_context.emit_fact(
                run_id,
                stage="page_ing",
                component="RecipeWriter",
                result="declined",
                reason="failed at page_ing",
                )
            return

        run_context.touch(
                run_id,
                agent="RecipeWriterAgent",
                action="softly-paged",
                domain="recipe",
                reason="File softly paged",
            )
        run_context.emit_fact(
                run_id,
                stage="paged",
                component="RecipeWriterAgent",
                result="ok",
                reason="File softly paged",
                )
        
        print("THIS IS RECIPE:",recipe_page)
        print("THIS IS CONFIDENCE:", confidence)

        event_bus.emit("recipe.softly_paged", 
            {
            "domain":"recipe",
            "recipe":recipe_page,
            "confidence":confidence,
            "run_id": run_id,
            }
        )
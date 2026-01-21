from hephis_core.services.detectors.recipe_detector import RecipeDetector
from hephis_core.infra.extractors.registry import extractor
from .from_tg import extract_recipe_from_tg_html
import logging

logger = logging.getLogger(__name__)

@extractor(domain="recipe", input_type="html")
def extract_recipe_from_html(html):
    
    result = RecipeDetector.detect_from_html(html)
    if not result:
        logger.warning("[recipe extractor] standart html failed",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"extractor-of-html",
                }
            )
    return result
       
    result = extract_recipe_from_tg_html(html)
    if not result:
        logger.warning("[recipe extractor] TG fall back failed",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"extractor-of-html",
                }
            )
        return None
    return result
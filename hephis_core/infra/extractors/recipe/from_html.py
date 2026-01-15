from hephis_core.services.detectors.recipe_detector import RecipeDetector
from hephis_core.infra.extractors.registry import extractor
from .from_tg import extract_recipe_from_tg_html

@extractor(domain="recipe", input_type="html")
def extract_recipe_from_html(html):
    try:
        result = RecipeDetector.detect_from_html(html)
        if result:
            return result
    except Exception as e:
        print("[recipe extractor] detector failed", e)
    
    try:
        result = extract_recipe_from_tg_html(html)
        if result:
            return result
    except Exception as e:
        print("[recipe extractor] TG fall back failed", e)

    return None
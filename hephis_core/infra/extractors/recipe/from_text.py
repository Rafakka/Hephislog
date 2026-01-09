
from hephis_core.services.detectors.recipe_detector import RecipeDetector
from hephis_core.infra.extractors.registry import extractor

@extractor(domain="recipe", input_type="text")
def extract_recipe_from_text(text: str):
    return RecipeDetector.detect_from_text(text)
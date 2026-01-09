from hephis_core.infra.extractors.registry import extractor
from hephis_core.services.detectors.recipe_detector import RecipeDetector

@extractor(domain="recipe", input_type="json")
def extract_recipe_from_json_recipe(obj):
    return RecipeDetector.detect_from_json(obj)
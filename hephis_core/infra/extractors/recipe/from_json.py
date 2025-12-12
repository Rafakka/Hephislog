from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action
from hephis_core.services.detectors.recipe_detector import RecipeDetector

@log_action(action="extract_recipe_from_json")
@extractor(domain="recipe", input_type="json")
def extract_recipe_from_json(obj):
    return RecipeDetector.detect_from_json(obj)
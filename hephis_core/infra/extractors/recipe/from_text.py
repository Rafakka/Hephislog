
from hephis_core.services.detectors.recipe_detector import RecipeDetector
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action


@log_action(action="extract_recipe_from_text")
@extractor(domain="recipe", input_type="text")
def extract_recipe_from_text(text: str):

    result = RecipeDetector.detect_from_text(text)

    if result:
        return result

    return None
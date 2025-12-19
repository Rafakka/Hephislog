from utils.file_setter import file_finder
from modules.recipe_normalizer.normalizer import recipe_normalizer


def test_normalizer_flow():
    finder_result = file_finder(folder_name="recipes_tg")

    print("\n--- FILE FINDER OUTPUT ---")
    print(finder_result)

    assert finder_result["success"] is True, "Could not retrieve JSON for normalization."

    raw_recipe = finder_result["data"]

    norm_result = recipe_normalizer(raw_recipe)

    print("\n--- NORMALIZER RESULT ---")
    print(norm_result)

    assert norm_result["success"] is True, "Recipe normalization failed."

    print("\n--- CLEANED RECIPE ---")
    print(norm_result["data"])

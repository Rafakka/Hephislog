from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action

@log_action(action="extract recipe from file")
@extractor(domain="recipe", input_type="file")
def extract_recipe_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "raw_content": content,
        "source": "file",
        "filename": os.path.basename(path)
    }
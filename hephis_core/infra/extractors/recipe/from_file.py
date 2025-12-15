import os
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action
from pathlib import Path

@log_action(action="extract_recipe_from_file")
@extractor(domain="recipe", input_type="file")
def extract_recipe_from_file(path):
    file_path = Path(path)

    if not file_path.exists() or not file_path.is_file():
        return None

    content = file_path.read_text(errors="ignore")

    return {
        "text": content,
        "source": "file",
        "filename": file_path.name
    }
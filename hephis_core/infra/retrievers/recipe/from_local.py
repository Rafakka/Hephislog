
from pathlib import Path
from hephis_core.infra.retrievers.registry import retriever
from hephis_core.utils.logger_decorator import log_action
from hephis_core.utils.file_setter import file_finder


BASE = Path("data/recipes")

@log_action(action="retrieve_recipe_from_local")
@retriever(domain="recipe", input_type="file")
def load_recipe_from_local(path: str) -> dict | None:
    """
    Load a recipe stored locally in data/recipes/<slug>
    """
    folder = BASE / path

    if not folder.exists() or not folder.is_dir():
        return None

    info = file_finder(str(folder))

    if info and info.get("success"):
        return info["data"]

    return None


@log_action(action="list_local_recipes")
@retriever(domain="recipe", input_type="list")
def list_local_recipes(_: str = "") -> list:
    """
    List all recipe folders and return metadata.
    """
    results = []

    for folder in BASE.iterdir():
        if folder.is_dir():
            info = file_finder(str(folder))

            if info.get("success"):
                data = info["data"]

                results.append({
                    "title": data.get("title", "Unknown"),
                    "slug": folder.name,
                    "path": info["file_path"]
                })

    return results

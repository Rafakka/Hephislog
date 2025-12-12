from pathlib import Path
from hephis_core.infra.retrievers.registry import retriever
from hephis_core.utils.retriever_utils import load_from_local, list_local
from hephis_core.utils.logger_decorator import log_action

BASE = Path("data/recipes")


@log_action(action="retrieve_recipe_from_local")
@retriever(domain="recipe", input_type="file")
def load_recipe(slug: str):
    return load_from_local(BASE, slug)


@log_action(action="list_local_recipe")
@retriever(domain="recipe", input_type="list")
def list_recipe(_: str = ""):
    return list_local(BASE)
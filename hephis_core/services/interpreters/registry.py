from hephis_core.services.interpreters.recipe import RecipeInterpreter
from hephis_core.services.interpreters.music import MusicInterpreter

INTERPRETER_MAP = {
    "recipe": RecipeInterpreter(),
    "music": MusicInterpreter(),
}
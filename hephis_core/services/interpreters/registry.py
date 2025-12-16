from hephis_core.services.interpreters.recipe_interpreter import RecipeInterpreter
from hephis_core.services.interpreters.music_interpreter import MusicInterpreter

INTERPRETER_MAP = {
    "recipe": RecipeInterpreter(),
    "music": MusicInterpreter(),
}
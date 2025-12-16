from hephis_core.services.interpreters.base import Interpreter

class RecipeInterpreter(Interpreter):
    domain = "recipe"

    def interpret(self, detected: dict, env):
        if not detected:
            return None

        title = detected.get("title") or "Untitled Recipe"

        return {
            "domain": "recipe",
            "title": title,
            "ingredients": detected.get("ingredients", []),
            "steps": detected.get("steps", []),
            "source": detected.get("source", "unknown"),
            "confidence": env.smells.get("recipe", 0.5),
            "env": env.snapshot(),
        }
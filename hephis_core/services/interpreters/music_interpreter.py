from hephis_core.services.interpreters.base import Interpreter

class MusicInterpreter(Interpreter):
    domain = "music"

    def interpret(self, detected: dict, env):
        if not detected:
            return None

        return {
            "domain": "music",
            "title": detected.get("title", "Untitled Song"),
            "sections": detected.get("sections", []),
            "source": detected.get("source", "unknown"),
            "confidence": env.smells.get("music", 0.5),
            "env": env.snapshot(),
        }
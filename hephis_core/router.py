from hephis_core.services.detectors.recipe_detector import RecipeDetector
from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.interpreters.registry import INTERPRETER_MAP


def choose_candidates(env):
    """
    Decide domain priority based on smells.
    Smells advise, never exclude.
    """

    smells = env.smells

    scores = {
        "recipe": smells.get("recipe", 0),
        "music": smells.get("music", 0),
    }

    # If no smell at all, try everything
    if all(score == 0 for score in scores.values()):
        return ["recipe", "music"]

    # Order by confidence (descending)
    return sorted(scores, key=lambda k: scores[k], reverse=True)


DETECTOR_MAP = {
    "recipe": RecipeDetector,
    "music": ChordDetector,
}


def route(raw_input, env):
    """
    Route input through detectors and interpreters.
    Returns interpreted result or None.
    """

    candidates = choose_candidates(env)

    for domain in candidates:
        detector = DETECTOR_MAP.get(domain)
        interpreter = INTERPRETER_MAP.get(domain)

        if not detector or not interpreter:
            continue

        try:
            # --- detection ---
            if domain == "recipe":
                detected = (
                    detector.detect_from_text(raw_input)
                    or detector.detect_from_html(raw_input)
                    or detector.detect_from_json(raw_input)
                )

            elif domain == "music":
                detected = (
                    detector.detect(raw_input, "html")
                    or detector.detect(raw_input, "text")
                )

            else:
                detected = None

            if not detected:
                continue

            # --- interpretation ---
            interpreted = interpreter.interpret(detected, env)

            if interpreted:
                return interpreted

        except Exception:
            # detectors must fail silently here
            continue

    return None

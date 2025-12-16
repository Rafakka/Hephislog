from hephis_core.services.interpreters.registry import INTERPRETER_MAP

def route(raw_input, env):
    candidates = choose_candidates(env)

    for domain in candidates:
        detector = DETECTOR_MAP.get(domain)
        interpreter = INTERPRETER_MAP.get(domain)

        if not detector or not interpreter:
            continue

        try:
            # --- detection phase ---
            if domain == "recipe":
                detected = (
                    detector.detect_from_text(raw_input)
                    or detector.detect_from_html(raw_input)
                    or detector.detect_from_json(raw_input)
                )
            elif domain == "music":
                detected = detector.detect(raw_input, "text")
            else:
                detected = None

            if not detected:
                continue

            # --- interpretation phase ---
            interpreted = interpreter.interpret(detected, env)

            if interpreted:
                return interpreted

        except Exception:
            continue

    return None
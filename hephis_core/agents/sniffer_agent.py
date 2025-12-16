from hephis_core.environment import ENV

class SnifferAgent:

    def sniff(self, raw):
        if not isinstance(raw, str):
            return ENV.smells

        text = raw.lower()

        # --- HTML smell ---
        if "<html" in text or "<div" in text:
            ENV.add_smell("html", 0.9)

        # --- Recipe smell ---
        if "ingrediente" in text:
            ENV.add_smell("recipe", 0.6)
        
        if "modo de preparo" in text or "preparo" in text:
            ENV.add_smell("recipe", 0.8)

        # --- json smell ---
        if (text.startswith("{") and text.endswith("}")) or \
           (text.startswith("[") and text.endswith("]")):
            try:
                json.loads(text)
                ENV.add_smell("json", 0.9)
            except Exception:
                ENV.add_smell("json", 0.4)

        # --- Music smell ---
        if "[" in text and "]" in text:
            ENV.add_smell("music", 0.5)

        if any(chord in text for chord in [" am ", " em ", " g ", " c "]):
            ENV.add_smell("music", 0.4)

        # --- Risk smell ---
        if len(text) > 100_000:
            ENV.add_smell("huge_input", 1.0)

        return ENV.smells

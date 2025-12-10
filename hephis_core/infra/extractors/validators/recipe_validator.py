

def is_valid_recipe(self, raw):
        return (
            isinstance(raw, dict)
            and "ingredients" in raw
            and "steps" in raw
        )

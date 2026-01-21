
def evaluate_recipe(raw_recipe:dict, normalized:dict) -> dict:
    
    warnings = normalized.get("metada",{}).get("warnings") or []

    raw_ingredients = raw_recipe.get("ingredients") or []
    norm_ingredients = normalized.get("ingredients") or []

    raw_steps = raw_recipe.get("steps") or []
    norm_steps = normalized.get("steps") or []

    schema_fit = 1.0

    ingredients_fit = (
        len(norm_ingredients)/len(raw_ingredients)
        if raw_ingredients else 0.0
    )

    steps_fit =  (
        len(norm_steps)/len(raw_steps)
        if raw_steps else 0.0
    )

    warnings_penalty = min(len(warnings)*0.5, 0.3)

    overall = (
        schema_fit * 0.4 +
        ingredients_fit * 0.3 +
        steps_fit * 0.3
    ) - warnings_penalty

    return {
        "schema_fit":round(schema_fit, 3),
        "ingredients_fit":round(ingredients_fit,3),
        "steps_fit":round(steps_fit,3),
        "warning_penalty":round(warnings_penalty, 3),
        "overall":round(max(0.0, overall),3)
    }
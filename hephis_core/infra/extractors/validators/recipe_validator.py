

def is_valid_recipe(raw:dict)-> bool:
    if not raw:
        return False

    ingredients = raw.get("ingredients") or []
    steps = raw.get("steps") or []

    if not ingredients and not steps:
        return False
    
    return True
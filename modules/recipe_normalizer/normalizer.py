
import re
import hashlib

from datetime import datetime
from schemas.panaceia_schemas import RecipeSchema, IngredientSchema, UNIT_MAP, UNICODE_FRACTIONS

def parse_ingredient_line(line: str) -> dict:
    """
    Normalizes an ingredient line into:
    {
        "quantity": float | None,
        "unit": str | None,
        "name": str,
        "notes": str | None
    }
    """

    original = line
    line = line.strip().lower()

    quantity = None
    unit = None
    notes = None

    # ----------------------------------------
    # 1) UNICODE FRACTIONS (½, ¼, ¾…)
    # ----------------------------------------
    for uf, value in UNICODE_FRACTIONS.items():
        if line.startswith(uf):
            quantity = value
            line = line[len(uf):].strip()
            break

    # ----------------------------------------
    # 2) MIXED NUMBERS ("1 1/2")
    # ----------------------------------------
    if quantity is None:
        mixed = re.match(r'^(\d+)\s+(\d+/\d+)', line)
        if mixed:
            whole = int(mixed.group(1))
            num, den = mixed.group(2).split('/')
            quantity = whole + (int(num) / int(den))
            line = line[mixed.end():].strip()

    # ----------------------------------------
    # 3) FRACTION ONLY ("3/4")
    # ----------------------------------------
    if quantity is None:
        frac = re.match(r'^(\d+/\d+)', line)
        if frac:
            num, den = frac.group(1).split('/')
            quantity = int(num) / int(den)
            line = line[frac.end():].strip()

    # ----------------------------------------
    # 4) DECIMAL or INTEGER (1,5 → 1.5)
    # ----------------------------------------
    if quantity is None:
        num_match = re.match(r'^(\d+[.,]?\d*)', line)
        if num_match:
            num_text = num_match.group(1).replace(',', '.')
            try:
                quantity = float(num_text)
            except ValueError:
                quantity = None
            line = line[num_match.end():].strip()

    # ----------------------------------------
    # 5) UNIT MATCHING (longest-first)
    # ----------------------------------------
    for raw_unit in sorted(UNIT_MAP.keys(), key=len, reverse=True):
        if raw_unit in line:
            unit = UNIT_MAP[raw_unit]
            line = line.replace(raw_unit, "").strip()
            break

    # ----------------------------------------
    # 6) NOTES (“(chá)”, “(sopa)”, etc.)
    # ----------------------------------------
    notes_match = re.search(r'\((.*?)\)', line)
    if notes_match:
        notes = notes_match.group(1).strip()
        line = re.sub(r'\(.*?\)', '', line).strip()

    # ----------------------------------------
    # 7) NAME CLEANING
    # ----------------------------------------
    name = line

    # Remove leftover "de " at start
    if name.startswith("de "):
        name = name[3:].strip()

    # Clean excess spaces
    name = re.sub(r'\s+', ' ', name).strip()

    # ----------------------------------------
    # 8) SAFETY FALLBACK (never return empty name)
    # ----------------------------------------
    if not name:
        name = original.strip()

    # ----------------------------------------
    # FINAL DICT
    # ----------------------------------------
    return {
        "quantity": quantity,
        "unit": unit,
        "name": name
    }


def recipe_normalizer(recipe: dict, schema_version="1.0.0", module_version="1.0.0"):

    if not isinstance(recipe, dict):
        return {
            "success": False,
            "data": None,
            "error": "DataFormatError",
            "message": "Input is not a dictionary. Cannot normalize."
        }

    normalized = {}
    warnings = []

    try:
        title = recipe["title"]
        normalized["name"] = title.strip().lower().title()
    except KeyError:
        return {
            "success": False,
            "data": None,
            "error": "MissingField",
            "message": "Recipe is missing required field: title"
        }
    
    try:
        steps_list = recipe["steps"]
    except KeyError:
        return {
            "success": False,
            "data": None,
            "error": "MissingField",
            "message": "Recipe is missing required field: steps"
        }

    cleaned_steps = []

    for step in steps_list:
        step = re.sub(r'^\s*\d+[\.\)\-]?\s*', '', step)
        step = step.strip()
        if step:
            cleaned_steps.append(step)

    # Join list into a single text block
    normalized["steps"] = "\n\n".join(cleaned_steps)

    try:
        raw_ingredients = recipe["ingredients"]
    except KeyError:
        return {
            "success": False,
            "data": None,
            "error": "MissingField",
            "message": "Recipe is missing required field: ingredients"
        }

    cleaned_ingredients = []

    for ing_line in raw_ingredients:
        parsed = parse_ingredient_line(ing_line)

        ingredient_obj = {
            "name": parsed["name"],
            "quantity": parsed["quantity"],
            "unit": parsed["unit"]
        }

        if parsed.get("notes"):
            warnings.append(f"Note detected in ingredient '{parsed['name']}': {parsed['notes']}")

        cleaned_ingredients.append(ingredient_obj)

    normalized["ingredients"] = cleaned_ingredients

    normalized["spices"] = []

    try:
        model = RecipeSchema(**normalized)
    except Exception as e:
        return {
            "success": False,
            "data": normalized,
            "error": "ValidationError",
            "message": str(e)
        }

    validated = model.model_dump()


    # ------------------------------------------
    # 5) METADATA & CHECKSUM
    # ------------------------------------------
    canonical_json = str(validated).encode("utf-8")
    checksum = hashlib.sha1(canonical_json).hexdigest()

    validated["_metadata"] = {
        "schema_version": schema_version,
        "module_version": module_version,
        "normalized_at": datetime.utcnow().isoformat() + "Z",
        "checksum": checksum,
        "warnings": warnings or None
    }


    # ------------------------------------------
    # 6) FINAL RETURN (STANDARD API SHAPE)
    # ------------------------------------------
    return {
        "success": True,
        "data": validated,
        "error": None,
        "message": "Recipe normalized successfully."
    }

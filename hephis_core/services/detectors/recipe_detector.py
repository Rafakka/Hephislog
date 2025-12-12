import json
import re
from typing import Optional, List, Dict


class RecipeDetector:

    # -------------------------------
    #  KEY FINDER
    # -------------------------------
    @staticmethod
    def _find_key(obj: dict, possible_keys: List[str]) -> Optional[str]:
        for key in possible_keys:
            if key in obj:
                return key
        return None

    # -------------------------------
    #  TITLE DETECTION
    # -------------------------------
    @staticmethod
    def find_possible_title(obj: dict) -> Optional[str]:
        title_keys = [
            "title", "titulo", "name", "recipe_title", "headline",
            "recipeName", "recipe_name"
        ]
        key = RecipeDetector._find_key(obj, title_keys)
        return obj[key] if key else None

    # -------------------------------
    #  INGREDIENT DETECTION
    # -------------------------------
    @staticmethod
    def find_possible_ingredients(obj: dict) -> Optional[List[str]]:
        ing_keys = [
            "ingredients", "ingredientes", "itens", "items",
            "ingredientLines", "ingredient_lines", "components"
        ]
        key = RecipeDetector._find_key(obj, ing_keys)
        if not key:
            return None

        ingredients = obj[key]

        # list of strings or dicts
        if isinstance(ingredients, list):
            cleaned = []
            for item in ingredients:
                if isinstance(item, str):
                    cleaned.append(item)
                elif isinstance(item, dict):
                    text = (
                        item.get("text") or
                        item.get("raw") or
                        item.get("name")
                    )
                    if text:
                        cleaned.append(text)
            return cleaned

        return None

    # -------------------------------
    #  STEP DETECTION
    # -------------------------------
    @staticmethod
    def find_possible_steps(obj: dict) -> Optional[List[str]]:
        step_keys = [
            "steps", "instrucoes", "modo_preparo", "preparo",
            "instructions", "directions", "method", "methodSteps"
        ]
        key = RecipeDetector._find_key(obj, step_keys)
        if not key:
            return None

        steps = obj[key]

        if isinstance(steps, list):
            cleaned = []
            for s in steps:
                if isinstance(s, str):
                    cleaned.append(s)
                elif isinstance(s, dict):
                    text = (
                        s.get("text") or
                        s.get("step") or
                        s.get("instruction")
                    )
                    if text:
                        cleaned.append(text)
            return cleaned

        if isinstance(steps, str):
            return [steps]

        return None

    # -------------------------------
    #  JSON DETECTOR
    # -------------------------------
    @staticmethod
    def detect_from_json(obj: dict) -> Optional[dict]:
        if not isinstance(obj, dict):
            return None

        title = RecipeDetector.find_possible_title(obj)
        ing = RecipeDetector.find_possible_ingredients(obj)
        steps = RecipeDetector.find_possible_steps(obj)

        if not (title and ing and steps):
            return None

        return {
            "title": title,
            "ingredients": ing,
            "steps": steps,
            "source": "json_raw"
        }

    # -------------------------------
    #  TEXT DETECTOR
    # -------------------------------
    @staticmethod
    def detect_from_text(text: str) -> Optional[dict]:
        lines = text.lower().splitlines()
        ingredients = []
        steps = []
        mode = None

        for line in lines:
            if "ingrediente" in line:
                mode = "ing"
                continue
            if "preparo" in line or "modo" in line or "passo" in line:
                mode = "steps"
                continue

            line = line.strip("-• ").strip()
            if not line:
                continue

            if mode == "ing":
                ingredients.append(line)
            elif mode == "steps":
                cleaned = re.sub(r"^\d+[\.\)]?\s*", "", line)
                steps.append(cleaned)

        if ingredients or steps:
            return {
                "title": "Untitled Recipe from Text",
                "ingredients": ingredients,
                "steps": steps,
                "source": "text_raw"
            }

        return None

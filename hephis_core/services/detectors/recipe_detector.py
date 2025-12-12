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
    
    @staticmethod
    def _extract_json_ld_recipe(soup: BeautifulSoup) -> Optional[dict]:
        scripts = soup.find_all("script", type="application/ld+json")

        for tag in scripts:
            try:
                data = json.loads(tag.string or "")
            except Exception:
                continue

            # Some sites wrap data in a list
            if isinstance(data, list):
                for item in data:
                    recipe = RecipeDetector._parse_json_ld_recipe(item)
                    if recipe:
                        return recipe
            else:
                recipe = RecipeDetector._parse_json_ld_recipe(data)
                if recipe:
                    return recipe

        return None

    @staticmethod
    def _parse_json_ld_recipe(data: dict) -> Optional[dict]:
        """
        Normalizes JSON-LD Recipe format to raw recipe structure.
        """
        if not isinstance(data, dict):
            return None

        # JSON-LD uses "@type"
        if data.get("@type") not in ("Recipe", "recipe"):
            return None

        title = data.get("name")
        ingredients = data.get("recipeIngredient") or data.get("ingredients")
        steps = data.get("recipeInstructions")

        # RecipeInstructions may be list of dicts: [{"text": "..."}]
        if isinstance(steps, list):
            cleaned = []
            for s in steps:
                cleaned.append(s.get("text") if isinstance(s, dict) else s)
            steps = cleaned

        if not (title and ingredients and steps):
            return None

        return {
            "title": title,
            "ingredients": ingredients,
            "steps": steps,
            "source": "json_ld"
        }

    @staticmethod
    def _extract_microdata_recipe(soup: BeautifulSoup) -> Optional[dict]:
        title = None
        title_tag = soup.find(attrs={"itemprop": "name"})
        if title_tag:
            title = title_tag.get_text(strip=True)

        ingredients = [
            ing.get_text(strip=True)
            for ing in soup.find_all(attrs={"itemprop": "recipeIngredient"})
        ]

        steps = [
            step.get_text(" ", strip=True)
            for step in soup.find_all(attrs={"itemprop": "recipeInstructions"})
        ]

        if title and ingredients and steps:
            return {
                "title": title,
                "ingredients": ingredients,
                "steps": steps,
                "source": "microdata"
            }

        return None
    
    @staticmethod
    def _extract_generic_html_recipe(soup: BeautifulSoup) -> Optional[dict]:
        text = soup.get_text(" ", strip=True).lower()

        # Quick signal check
        if "ingrediente" not in text or "preparo" not in text:
            return None

        # Ingredients
        ingredients = []
        ing_header = soup.find(lambda tag: tag.name in ("h2", "h3") and "ingred" in tag.text.lower())

        if ing_header:
            ul = ing_header.find_next("ul")
            if ul:
                for li in ul.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt:
                        ingredients.append(txt)

        # Steps
        steps = []
        prep_header = soup.find(lambda tag: tag.name in ("h2", "h3") and "preparo" in tag.text.lower())

        if prep_header:
            ol = prep_header.find_next("ol")
            if ol:
                for li in ol.find_all("li"):
                    steps.append(li.get_text(" ", strip=True))

        if ingredients and steps:
            return {
                "title": "Untitled Recipe from HTML",
                "ingredients": ingredients,
                "steps": steps,
                "source": "html_generic"
            }

        return None

    @staticmethod
    def detect_from_html(html: str) -> Optional[dict]:
        """
            Universal HTML recipe detection:
            1) JSON-LD schema.org Recipe
            2) Microdata (itemprop attributes)
            3) Generic headings ("Ingredientes", "Modo de Preparo", etc.)
            Returns None if no structure is detected.
        """
    soup = BeautifulSoup(html, "html.parser")

    # -------------------------------------------
    # 1) JSON-LD extraction (most reliable)
    # -------------------------------------------
    ld_json = RecipeDetector._extract_json_ld_recipe(soup)
    if ld_json:
        return ld_json

    # -------------------------------------------
    # 2) Microdata extraction (itemprop attributes)
    # -------------------------------------------
    micro = RecipeDetector._extract_microdata_recipe(soup)
    if micro:
        return micro

    # -------------------------------------------
    # 3) Generic HTML structure extraction
    #    (fallback heuristic)
    # -------------------------------------------
    generic = RecipeDetector._extract_generic_html_recipe(soup)
    if generic:
        return generic

    return None
    

    ROUTES = {
    "json": detect_from_json,
    "text": detect_from_text,
    "html": detect_from_html
    }   

    @staticmethod
    def detect(data, input_type: str):
        if input_type in RecipeDetector.ROUTES:
            fn = RecipeDetector.ROUTES[input_type]
            raw = fn(data)
            if raw:
                return raw
        
        return None
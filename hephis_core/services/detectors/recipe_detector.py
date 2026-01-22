from bs4 import BeautifulSoup
import json
import re
from typing import Optional, List, Dict


class RecipeDetector:


    INGREDIENTS_KEYWORDS = {
    "sal","açucar","oleo","azeite","farinha",
    "manteiga","margarina","ovos","cebola","fermento",
    "agua","leite","batatas","alho"
    }

    COOKING_VERBS = {
        "misturar","assar","sovar","adicionar","cortar",
        "esquentar","grelhar","cozinhar","fritar","ferver",
        "mexer","amassar",
        }

    QUANTITY_RE = re.compile (
        r"\b\d+(?:[.,]\d+)?\s*(?:copo|copos|pitada|colher|colheres|kg|g|ml|l)\b",
        re.IGNORECASE
    )


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

        lower_lines = text.lower().splitlines()
        orig_lines = text.splitlines()

        ingredients = []
        steps = []
        mode = None

        for low, orig in zip(lower_lines, orig_lines):

            if "ingrediente" in low:
                mode = "ing"
                continue

            if "preparo" in low or "modo" in low or "passo" in low:
                mode = "steps"
                continue

            cleaned_line = orig.strip("-• ").strip()
            if not cleaned_line:
                continue

            if mode == "ing":
                ingredients.append(cleaned_line)

            elif mode == "steps":
                step_text = re.sub(r"^\d+[\.\)]?\s*", "", cleaned_line)
                steps.append(step_text)

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

    # -------------------------------
    #  TEXT DETECTOR
    # -------------------------------
    @staticmethod
    def ingredient_signal(obj:dict) -> dict | None:
        key = RecipeDetector._find_key(obj, ["ingredients", "ingredientes", "itens", "items",
            "ingredientLines", "ingredient_lines", "components"])
        
        if not key:
            return None
        
        value = obj.get(key)
        
        if not value:
            return None
        
        return {
            "key":key,
            "type":type(value).__name__,
            "count":len(value) if isinstance(value, list) else 1
        }

    @staticmethod
    def recipe_ratio(text:str) -> float:
        if not text or not isinstance(text, str):
            return 0.0
        
        score = 0.0
        lowered = text.lower()

        ingredient_hint = sum(
            1 for k in RecipeDetector.INGREDIENTS_KEYWORDS if k in lowered
        )
        score += min(ingredient_hint*0.1, 0.4)

        quantity_hints =len(RecipeDetector.QUANTITY_RE.findall(lowered))
        score += min(quantity_hints * 0.2,0.4)

        verb_hints = sum (
            1 for v in RecipeDetector.COOKING_VERBS if v in lowered
        )
        score += min (verb_hints*0.1,0.3)

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) >= 3:
            avg_len = sum(len(l) for l in lines) / len(lines)
            if avg_len <60:
                score += 0.1
                
        return min(score, 1.0)
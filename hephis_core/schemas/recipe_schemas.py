"""

schemas.py

Defines the data validation schemas used across the application.

These Pydantic models enforce strict type validation for API inputs and outputs,
ensuring that all data sent to or from the database follows the expected format.

Author: Rafael Kaher

"""
from pydantic import BaseModel, StrictStr, StrictFloat, Field, ConfigDict
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class IngredientSchema(BaseModel):
    """

    Represents the schema for an ingredient object used in recipes.

    Attributes:
        name (StrictStr): Ingredient name.
        quantity (StrictFloat): Ingredient amount (must be a float).
        unit (StrictStr): Measurement unit (e.g., "Grm", "Mls", "Cp").

    Example:
        ```python
        IngredientSchema(
        name="Flour",
        quantity=200.0,
        unit="Grm"
        )
        ```
    """
    model_config = ConfigDict(extra="ignore")
    
    name: StrictStr
    quantity: Optional[StrictFloat] = None
    unit: Optional[StrictStr] = None


class RecipeSchema(BaseModel):
    """

    Defines the schema for a complete recipe,
    including its basic information and a list of ingredients.

    Attributes:
        name (StrictStr): Recipe name.
        steps (StrictStr): Preparation instructions.
        ingredients (List[IngredientSchema]): List of ingredients following the IngredientSchema model.

    Usage Example:
        ```python
        RecipeSchema(
            name="Pancakes",
            steps="Mix ingredients and fry until golden.",
            ingredients=[
                IngredientSchema(name="Flour", quantity=200.0, unit="Grm"),
                IngredientSchema(name="Milk", quantity=250.0, unit="Mls")
            ]
        )
        ```
    """
    model_config = ConfigDict(extra="ignore")

    name: StrictStr
    steps: StrictStr
    ingredients: List[IngredientSchema]
    spices: List[StrictStr] = []
    source: str
    


class SpiceSchema(BaseModel):
    """
    Represents a spice object with all contextual attributes used for learning and suggestions.
    
    Attributes:
        name (str): Spice name.
        flavor_profile (str): Description of its taste (e.g., "warm and sweet").
        recommended_quantity (str): Suggested usage, e.g., "1 tsp per 500g".
        pairs_with_ingredients (List[str]): Ingredients it matches with.
        pairs_with_recipes (List[str]): Recipes it commonly appears in.
    """

    name: StrictStr
    flavor_profile: Optional[StrictStr] = None
    recommended_quantity: Optional[StrictStr] = None
    pairs_with_ingredients: List[StrictStr] = Field(default_factory=list)
    pairs_with_recipes: List[StrictStr] = Field(default_factory=list)

UNIT_MAP = {
    "xicara": "Xca",
    "xicaras": "Xcas",
    "chicara": "Xca",
    "chicaras": "Xcas",

    "copo": "Cp",
    "copos": "Cps",
    "cps": "Cps",

    "colher de sopa": "Cl Sopa",
    "colheres de sopa": "Cls Sopa",
    "colher": "Cl",
    "colheres": "Cls",

    "colher de cha": "Cl Chá",
    "colheres de cha": "Cls Chá",

    "colher de sobremesa": "Cl SobreMs",
    "colheres de sobremesa": "Cls SobreMs",

    "grama": "g",
    "gramas": "Grm",
    "gramos": "Grm",
    "gram": "Grm",
    "gms": "Grm",
    "g": "g",

    "kg": "Kg",
    "kilo": "Kg",
    "kilos": "Kgs",
    "quilo": "Kg",
    "quilos": "Kgs",

    "ml": "Ml",
    "mls": "Mls",
    "mililitro": "Ml",
    "mililitros": "Mls",

    "l": "L",
    "litro": "L",
    "litros": "Ls",
    
    "pitada": "Pt",
    "unidade": "Unit"
}

UNICODE_FRACTIONS = {
    "½": 0.5,
    "¼": 0.25,
    "¾": 0.75,
    "⅓": 1/3,
    "⅔": 2/3,
    "⅛": 1/8,
}

def normalize_raw_text(raw_text) -> str:
    if raw_text is None:
        return ""
    
    if isinstance(raw_text, str):
        return raw_text.strip()
    if isinstance(raw_text, list):
        return "\n".join(
            str(x).strip()
            for x in raw_text
            if x
        )
    return str(raw_text)

def build_recipe_page(
    raw_recipe:dict | str,
    *,
    run_id:str,
    confidence:float,
    source:str | None,
) -> dict | None:

    warnings:list[str] = []

    if isinstance(raw_recipe, dict) and {"title","ingredients","steps"} <= raw_recipe.keys():
        
        Recipe_page = {
        "type":"recipe_page",
        "title":raw_recipe.get("title"),
        "ingredients":raw_recipe.get("ingredients",[]),
        "steps":raw_recipe.get("steps",[]),
        "raw_text":None,

        "structured":{
            "ingredients":[],
            "spices":[],
        },

        "source":source,
        "confidence":confidence,
        "run_id":run_id,

        "metadata": {
            "language":"pt",
            "warnings":["Bypassed heuritic parsing(already structured)"],
            "unit_system":"metric",
            },
        }

        return Recipe_page
    
    if isinstance(raw_recipe,dict):
        raw_text = normalize_raw_text(raw_recipe)
    else:
        raw_text = raw_recipe
    
    if not raw_text or not isinstance(raw_text, str):
        logger.warning("Missing raw_text or raw_text not string",
            extra={
                    "path":"recipe_schema.py",
                    "event":"recipe-writing",
                }
            )
        return
    
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    title = lines[0] if lines else None

    ingredients = []
    steps = []

    for line in lines[1:]:
        if any(x in line.lower() for x in ["colher", "xicara","g","kg","ml"]):
            ingredients.append(line)
        else:
            steps.append(line)
    
    if not ingredients:
        warnings.append("No ingredients detected.")
    
    if not steps:
        warnings.append("No steps detected.")

    structured = {
        "ingredients":[],
        "spices":[]
    }

    RecipePage = {
        "type":"recipe_page",
        "title":title,
        "ingredients":ingredients,
        "steps":steps,
        "raw_text":raw_text,

        "structured":structured,

        "source":source,
        "confidence":confidence,
        "run_id":run_id,

        "metadata": {
            "language":"pt",
            "warnings":warnings,
            "unit_system":"metric",
        },
    }

    return RecipePage

from hephis_core.utils.utils import extract_text
from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.detectors.recipe_detector import RecipeDetector
from hephis_core.services.detectors.field_detector import html_ratio, plain_text_ratio
from hephis_core.contracts.semantic_data_shaper import ContentProfile
import math
from typing import Dict

class FieldEvaluatorCore:
    def __init__(self, detectors):
        self.detectors = detectors
    
    def _entropy(self, ratios:Dict[str,float])->float:
        return - sum(
            p*math.log(p,2)
            for p in ratios.values()
            if p > 0
        )

    
    def evaluate(self, raw) -> dict[str, float]:
        text = extract_text(raw)
        lines = text.splitlines()

        scores = {
            "html":0,
            "text":0,
            "music":0,
            "recipe":0,
        }

        for line in lines:
            scores["music"] += ChordDetector.chord_ratio(line)
            scores["html"] += html_ratio(line)
            scores["recipe"] += RecipeDetector.recipe_ratio(line)
            scores["text"] += plain_text_ratio(line)
            
        total = sum(scores.values()) or 1.0
        ratios = {k: v / total for k, v in scores.items()}

        dominant = max(ratios, key=ratios.get)
        confidence = ratios[dominant]

        entropy = self._entropy(ratios)

        return ContentProfile(
            ratios=ratios,
            dominant=dominant,
            confidence=confidence,
            entropy=entropy,
        )

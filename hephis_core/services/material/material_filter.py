import re
from typing import List
from uuid import uuid4

from hephis_core.schemas.material_schema import MaterialChunk
from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.detectors.recipe_detector import RecipeDetector

class MaterialFilter:

    def looks_like_sentence(self, text:str) -> bool:
        return len(text.split()) > 3 and not self.ChordDetector.looks_like_chord_line(text)

    def __assign_signals(self, chunk:MaterialChunk):
        text = chunk.text

        chunk.signals["length"] = len(text)
        chunk.signals["token_count"] = len(text.split())
        chunk.signals["has_numbers"] = any(c.isdigit() for c in text)
        chunk.signals["has_symbols"] = bool(re.search(r"[#b/]",text))

    def _assign_hints(self, chunk:MaterialChunk):
        text = chunk.text

        ratio = ChordDetector.chord_ratio(text)
        if ratio > 0:
            chunk.hints.append("music")
            chunk.signals["chord_like_ratio"] = ratio
        
        signal = None
        if isinstance(chunk.raw, dict):
            signal = RecipeDetector.ingredient_signal(chunk.raw)
     
        if signal:
            if "recipe" not in chunk.hints:
                chunk.hints.append("recipe")
            chunk.signals["recipe_structural_signal"] = signal
        
        recipe_score = RecipeDetector.recipe_ratio(text)

        if recipe_score > 0:
            if "recipe" not in chunk.hints:
                chunk.hints.append("recipe")
            chunk.signals["recipe_text_ratio"] = recipe_score
        
        if self.looks_like_sentence(text):
            chunk.hints.append("text")
        
        if not chunk.hints:
            chunk.hints.append("unknown")

    def split(self:str, source:str = "text") -> List[MaterialChunk]:
        if not text or not isinstance(text,str):
            return []

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    chunks: List[MaterialChunk] = []

    for idx, line in enumerate(lines):
        chunk = MaterialChunk (
            id=str(uuid4()),
            text=line,
            source=source,
            order=idx,
        )

        self._assign_hints(chunk)
        self._assign_signals(chunk)

        chunks.append(chunk)

    return chunks
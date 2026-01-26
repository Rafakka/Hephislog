from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class SniffInference:
    smells:Dict[str, float]
    dominance_score: list[str]
    dominant:str | None
    confidence: float
    domain_hints: list[str]
    evidence: Dict[str, List[str]]
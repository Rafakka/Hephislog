
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class ContentProfile:
    ratios:Dict[str, float]
    dominant:str
    confidence:float
    entropy:float
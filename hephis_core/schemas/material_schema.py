from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class MaterialChunk:
    id:str
    text:str

    hints: List[str] = field(default_factory=list)
    signals: Dict[str, any] = field(default_factory=dict)

    source:str | None = None
    order:str | None = None

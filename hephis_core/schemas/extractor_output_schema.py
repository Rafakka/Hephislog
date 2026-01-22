from dataclasses import dataclass, field
from typing import List, Dict, Any, Literal

@dataclass
class ExtractionResult:
    schema:str
    status:Literal["success", "partial","fail"]
    confidence_delta:float

    produced_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=dict)

    notes: Dict[str,any] = field(default_factory=dict)
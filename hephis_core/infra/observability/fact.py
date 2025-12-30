from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional

ResultType = Literal ["ok","none","error","declined"]

@dataclass(frozen=True)
class Fact:
    run_id: str
    stage:str
    component:str
    result:ResultType
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
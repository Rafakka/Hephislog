from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .fact import Fact

@dataclass
class RunContext:
    run_id:str
    domain:str
    input_type:str

    started_at: datetime = field(default_factory=datetime.utcnow) 
    ended_at: Optional[datetime] = None
    facts:List[Fact] = field(default_factory=list)
    terminated_at_stage:Optional[str] = None

    def add_fact(self, fact: Fact) -> None:
        if fact.run_id != self.run_id:
            raise ValueError("Fact run_id does not matche RunContext.")
        self.facts.append(fact)

    def terminate(self, stage:str) -> None:
        if self.ended_at is not None:
            return
        self.terminated_at_stage = stage
        self.ended_at = datetime.utcnow()

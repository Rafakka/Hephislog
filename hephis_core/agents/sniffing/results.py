from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

@dataclass
class SniffResult:
    stage: str  # "pre_extract" | "post_extract"
    smells: Dict[str, float] = field(default_factory=dict)
    evidence: Dict[str, List[str]] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def add(self, name: str, score: float, reason: str | None = None):
        """
        Add or reinforce a smell.
        """
        current = self.smells.get(name, 0.0)
        self.smells[name] = max(current, score)

        if reason:
            self.evidence.setdefault(name, []).append(reason)

    def snapshot(self) -> dict:
        return {
            "stage": self.stage,
            "smells": self.smells,
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat(),
        }

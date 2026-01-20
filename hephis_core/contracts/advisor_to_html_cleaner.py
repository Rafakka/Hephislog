from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass(frozen=True)
class HtmlCleaningAdvice:
    version:int
    cleaning:str
    reason:str

@dataclass(frozen=True)
class AdvisorToHtmlCleanerMessage:
    EVENT = "system.advisor.to.html.cleaner"

    run_id:str
    stage:str
    raw:dict
    advice:HtmlCleaningAdvice

    smells:Dict[str, float]
    semantic_advice:Optional[dict] = None
    semantic_scores:Dict[str, float] = None

    source:Optional[str] = None
    domain_hint:List[str] = field(default_factory=list)

    @classmethod
    def from_advisor(
        cls,
        *,
        run_id:str,
        raw:str,
        cleaning:str,
        reason:str,
        smells:Dict[str, float],
        semantic_advice:Optional[dict] = None,
        domain_hint:Optional[List[str]] = None,
        source:Optional[str] = None,
    ):
        cls._validate_inputs(
            run_id,
            raw,
            cleaning,
            smells,
        )

        return cls(
            run_id=run_id,
            stage="material_raw",
            raw=raw,
            advice=HtmlCleaningAdvice(
                version=1,
                cleaning=cleaning,
                reason=reason,
            ),
            smells=smells,
            semantic_advice=semantic_advice,
            source=source,
            domain_hint=domain_hint or []
        )

    @staticmethod
    def _validate_inputs(
            run_id,
            raw,
            cleaning,
            smells,
        ):

            assert run_id, "run_id is required"
            assert isinstance(raw, dict), "raw must be dict"
            assert cleaning in("none","light","heavy")
            assert isinstance(smells, dict)

    def to_event(self) -> dict:
        return {
                "run_id":self.run_id,
                "stage":self.stage,
                "raw":self.raw,
                "advice":{
                    "version":self.advice.version,
                    "cleaning":self.advice.cleaning,
                    "reason":self.advice.reason,
                    },
                "smells":self.smells,
                "semantic_advice":self.semantic_advice,
                "source":self.source,
                "domain_hint":self.domain_hint,
                }

    @classmethod
    def from_event(cls, payload:dict) -> "AdvisorToHtmlCleanerMessage":
        advice = payload["advice"]
        return cls(
            run_id=payload["run_id"],
            stage=payload["stage"],
            raw=payload["raw"],
            advice=HtmlCleaningAdvice(
                version=advice["version"],
                cleaning=advice["cleaning"],
                reason=advice["reason"],
            ),
            smells=payload.get("smells",{}),
            semantic_advice=payload.get("semantic_advice",{}),
            source=payload.get("source"),
            domain_hint=payload.get("domain_hint",[]),
        )
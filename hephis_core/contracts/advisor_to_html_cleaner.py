from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass(frozen=True)
class HtmlCleaningAdvice:
    version:int
    cleaning:str
    reason:str
    html_smell:float

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
        html_smell:float,
        smells:Dict[str, float],
        semantic_advice:Optional[dict] = None,
        semantic_scores:Optional[Dict[str, float]] = None,
        domain_hint:Optional[List[str]] = None,
        source:Optional[str] = None,
    ):
        cls._validate_inputs(
            run_id,
            raw,
            cleaning,
            html_smell,
            smells,
            semantic_scores,
        )

        return cls(
            run_id=run_id,
            stage="material_raw",
            raw=raw,
            advice=HtmlCleaningAdvice(
                version=1,
                cleaning=cleaning,
                reason=reason,
                html_smell=html_smell,
            ),
            smells=smells,
            semantic_advice=semantic_advice,
            semantic_scores=semantic_scores,
            source=source,
            domain_hint=domain_hint or []
        )

    @staticmethod
    def _validate_inputs(
            run_id,
            raw,
            cleaning,
            html_smell,
            smells,
            semantic_scores,
        ):

            assert run_id, "run_id is required"
            assert isinstance(raw, dict), "raw must be dict"
            assert cleaning in("none","light","heavy")
            assert isinstance(html_smell,(int,float))
            assert isinstance(smells, dict)
            assert isinstance(semantic_scores, dict)

    def to_event(self) -> dict:
        return {
                "run_id":self.run_id,
                "stage":self.stage,
                "raw":self.raw,
                "advice":{
                    "version":self.advice.version,
                    "cleaning":self.advice.cleaning,
                    "reason":self.advice.reason,
                    "html_smell":self.advice.html_smell,
                    },
                "smells":self.smells,
                "semantic_advice":self.semantic_advice,
                "semantic_scores":self.semantic_scores,
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
                html_smell=advice["html_smell"],
            ),
            smells=payload.get("smells",{}),
            semantic_advice=payload.get("semantic_advice",{}),
            semantic_scores=payload.get("semantic_scores",{}),
            source=payload.get("source"),
            domain_hint=payload.get("domain_hint",[]),
        )
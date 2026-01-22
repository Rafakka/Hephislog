
from hephis_core.agents.sniffing.inference import SniffInference
from hephis_core.services.detectors.raw_detectors import normalize_claims
from hephis_core.services.detectors.raw_detectors import (
    claim_file,
    claim_html,
    claim_json,
    claim_text,
    claim_url,
)
from typing import Dict, Any, Optional, Tuple

class SnifferCore:

    @staticmethod
    def _raw_claims(self, raw:Any)-> Dict[str, float]:
        claims = {}

        for domain, fn in {
            "url":claim_url,
            "html":claim_html,
            "file":claim_file,
            "json":claim_json,
            "text":claim_text,
        }.items():
            score = fn(raw)
            if score > 0:
                claims[domain] = score
        return claims

    @staticmethod
    def _merge_prior_smells(
        self,
        claims:Dict[str, float],
        prior_smells:Dict[str, float],
    ) -> Dict[str, float]:
        merged = dict(claims)

        for domain, weight in prior_smells.items():
            merged[domain] = merged.get(domain, 0.0) + weight * 0.5
        
        return merged
    
    @staticmethod
    def _apply_domain_hints(
        self,
        claims:Dict[str, float],
        domain_hint:List[str],
    ) -> Dict[str, float]:
        
        if not domain_hint:
            return claims
        
        biased = dict(claims)

        for domain in domain_hint:
            biased[domain] = biased.get(domain, 0.0) + 0.1
        return biased

    @staticmethod
    def _infer_dominance(
        self,
        smells:Dict[str, float],
    ) -> tuple[Optional[str], float]:
        
        if not smells:
            return None, 0.0
        
        sorted_items = sorted(smells.items(),key=lambda x:x[1], reverse=True)
        domain, top_score = sorted_items[0]
        
        if len (sorted_items) == 1:
            return dominant, top_score
        
        second_score = sorted_items[1][1]
        confidence = max(0.0, top_score - second_score)

        return domain, confidence

    @staticmethod
    def sniffing(
        self,
        raw:any,
        prior_smells:Optional[Dict[str,float]] = None,
        domain_hint:Optional[list[str]] = None,
        url_state:Optional[str] = None,
    )-> SniffInference:
    
        prior_smells = prior_smells or {}
        domain_hint = domain_hint or []

        claims = self._raw_claims(raw)
        claims = self._merge_prior_smells(claims, prior_smells)
        claims = self._apply_domain_hints(claims, domain_hint)

        smells = normalize_claims(claims)

        dominant, confidence = self._infer_dominance(smells)

        return SniffInference (
            smells=smells,
            dominant=dominant,
            confidence=confidence,
            domain_hints=domain_hint,
            url_stage=url_state,
            evidence={
                "raw_claims":claims,
                "prior_smells":prior_smells,
                "domain_hint":domain_hint,

            }
        )


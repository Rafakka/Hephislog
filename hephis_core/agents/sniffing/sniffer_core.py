
from hephis_core.agents.sniffing.inference import SniffInference
from hephis_core.services.detectors.raw_detectors import (
    claim_file,
    claim_html,
    claim_json,
    claim_text,
    claim_url,
    normalize_claims,
)
from typing import Dict, Any, Optional, Tuple, List
from hephis_core.services.detectors.raw_detectors import early_advice_raw_input

class SnifferCore:
    @staticmethod
    def _raw_claims(raw:Any)-> Dict[str, float]:
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
        claims:Dict[str, float],
        prior_smells:Dict[str, float],
    ) -> Dict[str, float]:
        merged = dict(claims)

        for domain, weight in prior_smells.items():
            merged[domain] = merged.get(domain, 0.0) + weight * 0.5
        
        return merged
    
    @staticmethod
    def _apply_domain_hints(
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
    
    def _merge_claims( base:dict[str,float], incoming:dict[str,float],*,weight:float =1.0) -> dict[str,float]:
        
        merged=dict(base)

        for domain, score in incoming.items():
            if domain in merged:
                merged[domain] = max(merged[domain], score*weight)
            else:
                merged[domain] =score*weight
        return merged

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

        claims = SnifferCore._raw_claims(raw=raw)
        claims = SnifferCore._merge_claims(base=claims,incoming=prior_smells,weight=0.7)

        if not domain_hint:
            early_claims = early_advice_raw_input(raw)
            claims = SnifferCore._merge_claims(base=claims,incoming=early_claims,weight=0.3)

        claims = SnifferCore._apply_domain_hints(claims=claims, domain_hint=domain_hint)
        claims = SnifferCore._merge_prior_smells(claims=claims, prior_smells=prior_smells)

        smells = normalize_claims(claims)

        dominant, confidence = SnifferCore._infer_dominance(smells=smells)

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


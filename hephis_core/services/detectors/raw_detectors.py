
import json
from urllib.parse import urlparse
from pathlib import Path

def normalize_claims(
        claims:dict[str,float],
        *,
        min_threshold: float = 0.05,
        max_score:float =1.0,
    ) -> dict[str, float]:
        
        if not claims:
            return {}
        
        clamped = {
            k: min(max(v,0.0), max_score)
            for k, v in claims.items()
            if v >= min_threshold
        }

        if not clamped:
            return {}
        
        strongest = max(clamped.values())

        if strongest == 0:
            return
        
        normalized = {
            k: round(v /strongest, 4)
            for k, v in clamped.items()
        }

        return normalized

def safe_score(value)->float:
    return float(value) if isinstance(value,(int, float)) else 0.0

def claim_str(value) -> float:
    score = 0.0
    if isinstance(value, str):
        score += 0.4
    return min(score, 1.0)

def claim_url(value: str) -> float:

    if not claim_str(value):
        return 0.0

    score = 0.0

    text = value.strip()
    result = urlparse(text)

    url = all([result.scheme in ("http", "https"), result.netloc])

    if url:
        score += 0.4
    
    return min(score, 1.0)
    

def claim_html(value) -> float:

    if not claim_str(value):
        return 0.0

    score = 0.0
    text = value.lower()

    if text.endswith((".html","html")):
        score += 0.4
    
    if "<" not in text and ">" not in text:
        score += 0.4

    return min(score, 1.0)

def claim_file(value):

    if not claim_str(value):
        return 0.0

    score = 0.0

    path = value.strip()

    url_hint = claim_url(path)
    
    html_hint = claim_html(path)
    
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            score += 0.4
    except:
            score += 0.0

    score -= safe_score(url_hint)
    score -= safe_score(html_hint)

    return min(score, 1.0)

def claim_json(value):

    score = 0.0

    if not isinstance(value, str):
        return 0.0
    try:
        json.loads(value)
        score = 0.4
    except:
        return min(score, 1.0)

def claim_text(value):

    if not isinstance(value, str):
        return 0.0

    if claim_url(value): return 0.0
    if claim_html(value): return 0.0
    if claim_json(value): return 0.0
    if claim_file(value): return 0.0

    return 0.4

def infer_smell_bias(claims):
    bias = {}

    if "url" in claims:
        bias["url"] = 0.9
        bias["html"] = 0.1
        bias["json"] = 0.1
        bias["text"] = 0.5
    
    if "file" in claims:
        bias["file"] = 0.8
        bias["text"] = 0.2

    if not claims:
        return {}
    
    return bias

RAW_DOMAIN_DETECTOR = {
    "file":claim_file,
    "url":claim_url,
    "json":claim_json,
    "html":claim_html,
    "text":claim_text,
}

EARLY_SMELL_MAX = 0.05
EARLY_SMELL_FACTOR = 0.5

def _cap_early_smell(value:float) -> float:
    return min(value*EARLY_SMELL_FACTOR, EARLY_SMELL_MAX )

def early_advice_raw_input(raw) -> dict[str, float]:
    claims = {}

    if isinstance(raw,str):
        if raw.startswith("http"):
            raw_score = 0.2
            claims["url"] = _cap_early_smell(raw_score)
            
        if "\n" in raw and len(raw) > 500:
            claims["text"] = 0.1

    capped = {
        domain: _cap_early_smell(score)
        for domain, score in claims.items()
    }

    return capped

def detect_raw_type(value, env):
    claims = early_advice_raw_input(value, env)

    if not claims:
        return "unknown"
    
    return max(claims.items(),key=lambda x:x[1])[0]
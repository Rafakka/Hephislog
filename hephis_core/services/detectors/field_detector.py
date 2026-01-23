from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.detectors.raw_detectors import claim_html, claim_text

def html_ratio(line:str) ->float:
    return claim_html(line)

def plain_text_ratio(line:str) -> float:

    if not isinstance(line, str) or not line.strip():
        return 0.0
    
    base = claim_text(line)
    if base == 0.0:
        return 0.0

    alpha = sum(c.alpha() for c in line)
    total = len(line)

    if total == 0:
        return 0.0
    
    alpha_ratio = alpha / total
    
    return min((base / 0.4)* alpha_ratio, 1.0)
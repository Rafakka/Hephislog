from dataclasses import dataclass
from hephis_core.services.cleaners.data_cleaner import clean_html_artifacts

@dataclass
class GarbageAnalysis:
    total_lenght:int
    removable_lenght:int
    removable_ratio:float
    signals:list[str]
    recommendation: str

        
def analyze_html_garbage(html:str) -> GarbageAnalysis:
    total_lenght = len(html)

    cleaned_preview = clean_html_artifacts(html)
    removed_len = total_lenght - len(cleaned_preview)

    ratio = removed_len / max(total_lenght,1)

    signals = []

    if ratio > 0.4:
        signals.append("high-garbage-ratio")
    
    if total_lenght >200_000:
        signals.append("very-large-html")
    
    recommendation = "heavy-path" if ratio > 0.4 else "fast-path"

    return GarbageAnalysis (
        total_lenght=total_lenght,
        removable_lenght=removed_len,
        removable_ratio=ratio,
        signals=signals,
        recommendation=recommendation,
    )


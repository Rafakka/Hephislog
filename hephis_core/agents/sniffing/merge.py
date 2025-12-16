from hephis_core.agents.sniffing.results import SniffResult

def merge_sniffs(*sniffs: SniffResult) -> SniffResult:
    merged = SniffResult(stage="merged")

    for sniff in sniffs:
        for name, score in sniffs.smells.items():
            merged.add (
                name, score, reason=f"{sniff.stage} signal"
            )
        for name, reasons in sniff.evidence.items():
            merged.evidence.setdefault(name,[]).extend(reasons)
    
    return merged


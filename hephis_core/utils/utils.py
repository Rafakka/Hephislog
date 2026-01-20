

class FakeFact:
    def __init__(self, stage, component, result):
        self.stage = stage
        self.component = component
        self.result = result

def extract_text(raw):
    if isinstance (raw, str):
        return raw
    if isinstance(raw, dict):
        return raw.get("text","")
    return ""

def get_score(scores:dict, key:str, default=0.0)-> float:
    value = scores.get(key, default)
    return float(value) if isinstance(value,(int, float)) else default

def _flatten_text(value) -> list[str]:
    texts = []

    if isinstance(value,str):
        texts.append(value)
    elif isinstance(value, list):
        for item in value:
            texts.extend(_flatten_text(item))
    elif isinstance(value, dict):
        for v in value.values():
            texts.extend(_flatten_text(v))
    return texts



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

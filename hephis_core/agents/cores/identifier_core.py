
class IdentifierCore:
    def __init__(self, detectors):
        self.detectors = detectors
    
    def normalize(self,claims):
        total = sum(claims.values())
        if not total:
            return {}
        return {k: v / total for k, v in claims.items()}

    def evaluate(self, value, smells=None, early=None):
        claims = {}

        for domain, fn in self.detectors.items():
            score = fn(value)            
            if score > 0:
                claims[domain] = score
            
        if early:
            for domain, score in early.items():
                claims[domain] = claims.get(domain,0) +score*0.5

        if smells:
            for domain, score in smells.items():
                claims[domain] = claims.get(domain,0) +score*0.3
            
        return self.normalize(claims)
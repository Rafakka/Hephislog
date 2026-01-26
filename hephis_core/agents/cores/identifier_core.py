class IdentifierCore:
    def __init__(self, detectors):
        self.detectors = detectors
    
    def normalize(self,claims:dict[str, float]) -> dict[str, float]:
        total = sum(claims.values())
        if not total:
            return {}
        return {k: v / total for k, v in claims.items()}

    def evaluate(self, value, sniference):

        claims = {}

        for domain, fn in self.detectors.items():
            score = fn(value)            
            if score > 0:
                claims[domain] = score
            
        if sniference and sniference.smells:
            for domain, score in sniference.smells.items():
                claims[domain] = claims.get(domain,0.0) +score*0.3
            
        beliefs = self.normalize(claims)

        return {
            "beliefs": beliefs,
            "ranked":sorted(
                beliefs.items(),
                key=lambda x: x[1],
                reverse=True
            ),
        }
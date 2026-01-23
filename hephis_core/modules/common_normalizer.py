

def normalize_domain_hint(domain_hint):
    if domain_hint is None:
        return []
    if isinstance(domain_hint,str):
        return[domain_hint]
    if isinstance(domain_hint,list):
        return domain_hint
    return []

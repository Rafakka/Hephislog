EXTRACTOR_REGISTRY = {}

def extractor(domain: str, input_type: str):
    """
    Decorator that registers an extractor function for a given domain and input type.
    """
    def decorator(func):
        if input_type not in EXTRACTOR_REGISTRY:
            EXTRACTOR_REGISTRY[input_type] = {}

        if domain not in EXTRACTOR_REGISTRY[input_type]:
            EXTRACTOR_REGISTRY[input_type][domain] = []

        EXTRACTOR_REGISTRY[input_type][domain].append(func)

        return func

    return decorator

    
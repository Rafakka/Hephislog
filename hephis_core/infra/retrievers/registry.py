RETRIVER_REGISTRY = {}

def retriver(domain: str, input_type: str):
    """
    Decorator that registers an extractor function for a given domain and input type.
    """
    def decorator(func):
        if input_type not in RETRIVER_REGISTRY:
            RETRIVER_REGISTRY[input_type] = {}

        if domain not in RETRIVER_REGISTRY[input_type]:
            RETRIVER_REGISTRY[input_type][domain] = []

        RETRIVER_REGISTRY[input_type][domain].append(func)

        return func

    return decorator

    
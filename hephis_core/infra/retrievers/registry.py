RETRIEVER_REGISTRY = {}

def retriever(domain: str, input_type: str):
    """
    Decorator that registers an extractor function for a given domain and input type.
    """
    def decorator(func):
        if input_type not in RETRIEVER_REGISTRY:
            RETRIEVER_REGISTRY[input_type] = {}

        if domain not in RETRIEVER_REGISTRY[input_type]:
            RETRIEVER_REGISTRY[input_type][domain] = []

        RETRIEVER_REGISTRY[input_type][domain].append(func)

        return func

    return decorator

    
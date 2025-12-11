from hephis_core.infra.retrievers.registry import RETRIEVER_REGISTRY

def call_retrievers(domain:str, input_type:str, value=None):
    retrievers = RETRIEVER_REGISTRY.get(input_type,{}).get(domain,[])
    
    results = []

    for fn in retrievers:
        output = fn(value)
        if output:
            if isinstance(output, list):
                results.extend(output)
            else:
                results.append(output)
    
    return results
    
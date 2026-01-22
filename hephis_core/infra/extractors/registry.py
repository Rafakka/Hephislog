from hephis_core.schemas.extractor_output_schema import ExtractionResult

EXTRACTOR_REGISTRY = {}

def extractor(domain: str, input_type: str):
    """
    Decorator that registers an extractor function for a given domain and input type.
    """
    def decorator(func):
        EXTRACTOR_REGISTRY.setdefault(input_type,{}).setdefault(domain,[]).append(func)
        return func

    return decorator

def run_extractors(domain:str, input_type:str,value) -> list[ExtractionResult]:
    results = []

    extractors = EXTRACTOR_REGISTRY.get(input_type,{}).get(domain,[])

    for fn in extractors:
        try:
            result = fn(value)

            if isinstance(result, ExtractionResult):
                results.append(result)
            elif result is None:
                results.append(
                    ExtractionResult(
                        schema=fn.__name__,
                        status="fail",
                        confidence_delta=-0.1,
                        notes={"reason":"returned None"}
                    )
                )
            else:
                results.append(
                    ExtractionResult(
                        schema=fn.__name__,
                        status="success",
                        confidence_delta=0.3,
                        produced_fields=list(result.keys()) if isinstance(result,dict) else [],
                        notes={"legacy_output":True}
                    )
                )
        except Exception as exc:
            results.append(
                ExtractionResult(
                    schema=fn.__name__,
                    status="fail",
                    confidence_delta=-0.3,
                    notes={"expection":repr(exc)}
                )
            )

    return results
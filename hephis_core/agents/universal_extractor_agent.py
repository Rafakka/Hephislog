from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.infra.extractors.registry import EXTRACTOR_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC
from hephis_core.infra.extractors.common.from_html import fetch_url_as_html
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class UniversalExtractorAgent:

    validators = {
        "recipe": RECIPE,
        "music": MUSIC,
    }

    def __init__(self):
        print("4 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    def extract_any(self, value, raw_type):
        
        print("REGISTRY KEYS:",EXTRACTOR_REGISTRY.keys())

        tried_types = set()

        def try_type(value, type_):
            if not value or not type_:
                return None

            if type_ in tried_types:
                return None

            tried_types.add(type_)

            print("HTML EXTRACTORS",EXTRACTOR_REGISTRY.get("html"))

            extractors = EXTRACTOR_REGISTRY.get(type_, {})

            if not extractors:
                logger.warning("No extractors found!!!")
                return None
                
            for domain, fns in extractors.items():
                for fn in fns:
                    try:
                        raw = fn(value)
                    except Exception as exc:
                        logger.debug("Extraction function failed",
                        extra={
                                "agent":self.__class__.__name__,
                                "event":"extraction-by-universal-extractor",
                                "raw_type":type_,
                                "domain":domain,
                                "error":repr(exc),
                            }
                        )
                        continue

                    if raw is None:
                        continue

                    validator = self.validators.get(domain)
                    if not validator or validator(raw):
                        return domain, raw

            return None
        
        result = try_type(value, raw_type)
        if result:
            return result

        if raw_type == "url":
            html_value = fetch_url_as_html(value,"url")
            if html_value:
                return self.extract_any(value,"html")

        
        if raw_type != "html":
            try:
                html_value = fetch_url_as_html(value, raw_type)
            except Exception as exc:
                logger.debug(
                    "HTML conversion failed",
                    extra={
                    "agent":self.__class__.__name__,
                        "event":"extraction-by-universal-extractor",
                        "raw_type":raw_type,
                        "error":repr(exc),
                    },
                )

            if html_value:
                return try_type(html_value,"html")
        return None

    @on_event("system.input_identified")
    def handle_input(self, payload):
        print("RAN:",self.__class__.__name__) 
        input_value = payload.get("raw")
        input_type  = payload.get("raw_type")
        source = payload.get("source")
        run_id = extract_run_id(payload)

        print(f"THIS ARE THE VALUES--{input_value}--{input_type}--{source}--{run_id}")

        if not run_id:
            logger.warning("Source file missing run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"extraction-by-universal-extractor",
                    "payload_keys":list(payload.keys()),
                },
            )
            return

        if not input_value and not input_type:
            logger.warning("Source file has no valid data or nor type",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"extraction-by-universal-extractor",
                    "raw_type":input_type,
                    "raw_present":bool(input_value),
                }
            )
            run_context.touch(
                run_id,
                agent="UniversalExtractorAgent",
                action="extract_file",
                reason="missing_raw_or_type",
            )
            return

        try: 
            result = self.extract_any(input_value, input_type)
            print(f"THIS IS THE RESULT{result}")
            
        except Exception as exc:
            logger.exception("Extractor crashed",
            extra={
                "agent":self.__class__.__name__,
                    "event":"extraction-by-universal-extractor",
                    "action":"extract_file",
                    "reason":"exception",
                }
            )
        if not result:
            run_context.touch(
                run_id,
                agent="UniversalExtractorAgent",
                action="extract_file",
                reason="no_result",
            )
            run_context.emit_fact(
                    run_id,
                    stage="extractor",
                    component="UniversalExtractorAgent",
                    result="declined",
                    reason="no_result_extracted",
                    )
            return
            
        if result:
            domain, raw = result

            wrapped = {
                "stage":"material_raw",
                "raw":raw,
                "domain":domain,
                "source":source,
                "run_id":run_id,
            }

        if not domain or not raw:
            run_context.touch(
                run_id,
                agent="UniversalExtractorAgent",
                action="extract_file",
                reason="no_domain_or_and_no_raw",
            )
            run_context.emit_fact(
                    run_id,
                    stage="extractor",
                    component="UniversalExtractorAgent",
                    result="declined",
                    reason="no_domain_or_and_no_raw",
                    )
            return

        if not run_id:
            logger.warning("Source file has no valid id or run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"extraction-by-universal-extractor",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                    }
            )
            return

        run_context.touch(
                run_id,
                agent="UniversalExtractorAgent",
                action="extracted_file",
                domain=domain,
                reason="valid_file_type",
            )
        run_context.emit_fact(
                run_id,
                stage="extractor",
                component="UniversalExtractorAgent",
                result="accepted",
                reason="valid_file_type",
                )
        event_bus.emit(
            "system.extraction.completed",
            {   
                "raw":raw,
                "domain":domain,
                "run_id": run_id,
                "source":source,
            }
        )
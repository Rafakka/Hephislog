from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.infra.extractors.registry import EXTRACTOR_REGISTRY
from hephis_core.infra.extractors.validators import RECIPE, MUSIC
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.infra.extractors.main_extractor import _try_domain
import logging

logger = logging.getLogger(__name__)

class UniversalExtractorAgent:


    def __init__(self):
        print("4 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.input_identified")
    def handle_input(self, payload):
        print("RAN:",self.__class__.__name__) 
        raw = payload.get("raw")
        primary  = payload.get("raw_type")
        source = payload.get("source")
        run_id = extract_run_id(payload)

        if not run_id:
            logger.warning("Source file missing run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"extraction-by-universal-extractor",
                    "payload_keys":list(payload.keys()),
                },
            )
            return

        if not primary and not raw:
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


        result = _try_domain(raw, primary)
            
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
            
        domain, material_raw = result

        if not domain or not material_raw:
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

 
            run_context.touch(
                    run_id,
                    agent="UniversalExtractorAgent",
                    action="extracted_file",
                    domain_hint_extr=domain,
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
                    "stage":"material_raw",
                    "raw":raw,
                    "domain_hint_extr":domain_hint_extr,
                    "run_id": run_id,
                    "source":source,
                    "domain_hint":domain_hint,
                    "smells":payload.get("smells"),
                }
            )
            
        except Exception as exc:
            logger.exception("Extractor crashed",
            extra={
                "agent":self.__class__.__name__,
                    "event":"extraction-by-universal-extractor",
                    "action":"extract_file",
                    "reason":"exception",
                }
            )
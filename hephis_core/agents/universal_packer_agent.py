from hephis_core.services.packers.universal_packer import pack_data
from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
import logging

logger = logging.getLogger(__name__)

class UniversalPackerAgent:

    def __init__(self):
        print("8 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
    
    def data_assembler(run_id, source, normalized, confidence, domain):

        packed_data = {
            "normalized":normalized,
            "source":source,
            "confidence":confidence,
            "domain":domain,
            "run_id":run_id,
        }

        return packed_data

                
    @on_event("music.normalized")
    def handle_music(self, payload):
        print("MUSIC PACKING PAYLOAD")

        sheet =  payload.get("sheet")

        if not sheet:
            logger.warning("Normalizer received event without sheet.")
            return

        run_id = payload.get("run_id")

        if not run_id:
            logger.warning("run id from sheet is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"normalizing-music",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        normalized = sheet["normalized"]

        if not normalized:
            logger.warning("data from sheet is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"universal-packer",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        
        source = sheet["source"]

        if not source:
            logger.warning("source from sheet is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"universal-packer",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        confidence = payload.get("confidence")

        if not confidence:
            logger.warning("confidence from sheet is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"universal-packer",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return

        domain = payload.get("domain")

        if not domain:
            logger.warning("domain from sheet is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"universal-packer",
                    "raw_type":type(payload).__name__,
                    "raw_is_dict":isinstance(payload, dict),
                }
            )
            return
        
        packed_data = UniversalPackerAgent.data_assembler(run_id, normalized, source, confidence, domain)

        self._pack_domain(domain="music", packed_data=packed_data)

    @on_event("recipe.normalized")
    def handle_recipe(self, payload):
        print("PACKER RECIPE HANDLER CALLED",payload)

        normalized = payload.get("normalized")
        
        if not normalized:
            logger.warning("normalized failed delivering",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"packer-recipe",
                }
            )
            return

        run_id = payload.get("run_id")
        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"packer-recipe",
                }
            )
            return
    

        confidence = payload.get("confidence")
        
        if not confidence:
            logger.warning("confidence is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"packer-recipe",
                }
            )
            return
        
        domain = payload.get("domain")

        if not domain:
            logger.warning("domain is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"packer-recipe",
                }
            )
            return

        source = payload.get("source")

        if not source:
            logger.warning("source is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"packer-recipe",
                }
            )
            return
        
        scores = payload.get("scores")
        metadata = payload.get("metadata")
        
        packed_data = UniversalPackerAgent.data_assembler(run_id, source, normalized, confidence, domain)

        self._pack_domain(domain="recipe", packer_data= packed_data)

    def _pack_domain(self, domain: str, packer_data: dict):
        print("RAN:",self.__class__.__name__)

        normalized = packer_data.get("normalized")
        source = packer_data.get("source")
        confidence = packer_data.get("confidence")
        domain = packer_data.get("domain")
        run_id = packer_data.get("run_id")

        if isinstance(normalized, dict) and "data" in normalized:
            normalized_content = normalized["data"]
        else:
            normalized_content = normalized

        if hasattr(normalized_content, "model_dump"):
            serialized = normalized_content.model_dump()
        else:
            serialized = normalized_content

        title = normalized.get("name")

        packed = pack_data(domain, title, normalized_content)

        if not packed:
            run_context.touch(
                run_id,
                agent="UniversalPackerAgent",
                action="declined_file",
                domain=domain,
                reason="file_not_packed",
            )
            run_context.emit_fact(
                run_id,
                stage="packer",
                component="UniversalPackerAgent",
                result="declined",
                reason="file_not_packed",
                )
            return

        run_context.touch(
                run_id,
                agent="UniversalPackerAgent",
                action="packing_file",
                domain=domain,
                reason="valid_file_type",
            )
        run_context.emit_fact(
                run_id,
                stage="packing",
                component="UniversalPackerAgent",
                result="ok",
                reason="valid_file_type",
                )

        event_bus.emit(
            f"{domain}.pipeline_finished",
            {
                "normalized": serialized,
                "data": packed,
                "source": source,
                "domain":domain,
                "confidence": confidence,
                "run_id": run_id,
            }
        )
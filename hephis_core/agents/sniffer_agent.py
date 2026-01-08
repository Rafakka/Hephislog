import json
from hephis_core.events.decorators import on_event
from hephis_core.environment import ENV
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

class SnifferAgent:

    def __init__(self):
        print("1 - INIT:",self.__class__.__name__) 
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    def sniff(self, raw):
        
        if not isinstance(raw, str):
            logger.warning("Source file raw is no string",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"first-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return

        text = raw.lower()

        if"<html" in text or "<div" in text:
            ENV.add_smell("html",0.9)
        
        if "ingrediente" in text:
            ENV.add_smell("recipe",0.6)
        
        if "modo de preparo" in text or "preparo" in text:
            ENV.add_smell("recipe",0.8)
        
        if text.strip().startswith(("{","[")):
            try:
                json.loads(text)
                ENV.add_smell("json",0.9)
            except:
                ENV.add_smell("json",0.4)

        if any(chord in text for chord in["am","em","g","c"]):
            ENV.add_smell("music",0.5)        

        if len(text) > 100_000:
            ENV.add_smell("huge_input",1.0)
    
    @on_event("system.input_received")
    def sniff_input(self, payload: dict):

        raw = payload.get("input")
        run_id = extract_run_id(payload)

        if not run_id:
            logger.warning("Source file has no valid id or run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"first-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return
        
        ENV.reset()

        self.sniff(raw)

        run_context.touch(
                run_id=run_id,
                agent="SnifferAgent",
                action="scented_file",
                reason="advicing_type_of_file",
                event="first scenting",
            )
        run_context.emit_fact(
                run_id,
                stage="first-scenting",
                component="SnifferAgent",
                result="scented_file",
                reason="advicing_type_of_file",
                )

        event_bus.emit(
            "system.external_input",
            {
                "smells": ENV.smells,
                "snapshots": ENV.snapshot(),
                "run_id":run_id,
                "source": payload.get("source"),
                "raw":raw,
            }
        )

    @on_event("system.extraction.completed")
    def sniff_after_extraction(self, payload:dict):
        raw = payload["raw"]
        run_id = extract_run_id(payload)

        if not run_id:
            logger.error("Dropping event without run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"second-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return
        
        self.sniff(raw)

        run_context.touch(
                run_id,
                agent="SnifferAgent",
                action="re_scented_file",
                reason="advicing_on_extracted_file",
                event="second scenting",
            )

        run_context.emit_fact(
                run_id,
                stage="second-scenting",
                component="SnifferAgent",
                result="ok",
                reason="advicing_on_extracted_file",
                )

        event_bus.emit(
            "system.smells.post.extraction",
            {
                "smells": ENV.smells,
                "snapshots": ENV.snapshot(),
                "raw":raw,
                "run_id": run_id,
                "source": payload.get("source"),
            }
        )
import json
from hephis_core.events.decorators import on_event
from hephis_core.environment import ENV
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.detectors.raw_detectors import early_advice_raw_input
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

    def extract_sniff_text(self, raw) -> str | None:
        if isinstance(raw, dict):
            raw_extracted = (
                raw.get("text") 
                or raw.get("lyrics") 
                or raw.get("content") 
                )
            if raw_extracted:
                return raw_extracted
        if isinstance(raw, str):
            return raw
        else:
            logger.warning("Unsupported raw type",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"third-sniffing",
                }
            )
            return None

    def sniff(self, raw):

        text = self.extract_sniff_text(raw)
        
        if not text:
            logger.warning("raw is not sniffable",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"first-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw,dict),
                },
            )
            return

        text = text.lower()

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
        print("FIRST RAN:",self.__class__.__name__) 
        raw = payload.get("input")
        url_state = payload.get("url_state")
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
        
        advice = early_advice_raw_input(raw)

        domain_hint = advice["domain-hint"]
        url_stage = url_state or advice["url_stage"]
        
        if "url" in domain_hint:

            run_context.touch(
                    run_id=run_id,
                    agent="SnifferAgent",
                    action="rerouted_input",
                    reason="url-detected",
                    event="signalling-url-fetcher",
                )
            run_context.emit_fact(
                        run_id,
                        stage="semantic",
                        component="SnifferAgent",
                        result="ok",
                        reason="signalling-url-fetcher",
                        )
            event_bus.emit(
                "system.fetch_url_input",
                {
                    "run_id":run_id,
                    "source": payload.get("source"),
                    "raw":raw,
                    "url_state":"unresolved",
                    "domain_hint":domain_hint,
                    "origin":{
                    "type":"url",
                    "value":raw,
                    }
                }
            )
            return
        
        if domain_hint != "url":
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
                "domain_hint":domain_hint,
                "raw":raw,
            }
        )
        return

    @on_event("system.extraction.completed")
    def sniff_after_extraction(self, payload:dict):
        print("SECOND RAN:",self.__class__.__name__)
        raw = payload["raw"]
        run_id = extract_run_id(payload)
        stage = payload.get("stage")

        if stage != "material_raw":
            logger.error("Missing material_raw stage.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"second-sniffing",
                }
            )
            return

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
        
        if not raw:
            logger.error("Dropping event without data",
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
            "system.smells.to.advisor",
            {   
                "stage":stage,
                "smells": ENV.smells,
                "snapshots": ENV.snapshot(),
                "raw":raw,
                "run_id": run_id,
                "source": payload.get("source"),
            }
        )
    
    @on_event("system.cleaner.to.sniffer")
    def sniff_after_cleaning(self, payload:dict):
        print("THIRD RAN:",self.__class__.__name__)
        raw = payload["raw"]
        run_id = extract_run_id(payload)
        stage = payload.get("stage")
        incoming_smells = payload.get("smells",{})

        if stage != "material_cleaned":
            logger.error("Missing cleaning stage.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"third-sniffing",
                }
            )
            return

        if not run_id:
            logger.error("Dropping event without run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"third-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return

        for k, v in incoming_smells.items():
            ENV.add_smell(k,v)

        self.sniff(raw)

        text = self.extract_sniff_text(raw)

        if not text:
            logger.warning("no text on third sniffing to extract")
            return

        if ChordDetector.block_contains_chords(text):

            ENV.add_smell("music.semantic_confirmed", 1.0)
            stage = "post_clean_sniffing"

            run_context.touch(
                run_id,
                agent="SnifferAgent",
                action="re_scented_file",
                reason="advicing_on_cleaned_file_by_semantic",
                event="third scenting",
            )
            run_context.emit_fact(
                    run_id,
                    stage="sniffing",
                    component="SnifferAgent",
                    result="accepted",
                    reason="third-smell-semantic-after-cleaning",
            )

            print(F"CLEANED AND FINAL SCENTED: SMELL:{ENV.smells}")

            event_bus.emit(
                "system.smells.to.decisionagent",
                {   
                    "stage":"post_clean_sniffing",
                    "smells": ENV.smells,
                    "snapshots": ENV.snapshot(),
                    "raw":raw,
                    "run_id": run_id,
                    "source": payload.get("source"),
                }
            )
            return

        stage = "post_clean_sniffing"

        run_context.touch(
                run_id,
                agent="SnifferAgent",
                action="re_scented_file",
                reason="advicing_on_cleaned_file",
                event="third scenting",
            )

        run_context.emit_fact(
                run_id,
                stage="sniffing",
                component="SnifferAgent",
                result="accepted",
                reason="third-smell-after-cleaning",
                )

        print(F"CLEANED AND FINAL SCENTED: SMELL:{ENV.smells}")

        event_bus.emit(
            "system.smells.to.decisionagent",
            {   
                "stage":stage,
                "smells": ENV.smells,
                "snapshots": ENV.snapshot(),
                "raw":raw,
                "run_id": run_id,
                "source": payload.get("source"),
            }
        )
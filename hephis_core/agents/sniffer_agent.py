import json
from hephis_core.events.decorators import on_event
from hephis_core.environment import ENV
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.detectors.raw_detectors import early_advice_raw_input
from hephis_core.agents.sniffing.sniffing import extract_sniff_text, sniff
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

    
    def merged_smells(base,new,decay=0.5):
        merged = {}

        keys = set(base) | set(new)
        for k in keys:
            old = base.get(k, 0.0)
            fresh = new.get(k, 0.0)

            merged[k] = max(old*decay, fresh)

        return merged

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
        bias = advice.get("smell_bias,{}")
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
                    "raw":payload.get("input"),
                    "url_state":"unresolved",
                    "domain_hint":domain_hint,
                    "origin":{
                    "type":"url",
                    "value":raw,
                    }
                }
            )
            return
        
        if "url" not in domain_hint:
            ENV.reset()

        for smell, weight in bias.items():
            ENV.add_smell(smell, weight,source="early_advice")

        sniff(raw, agent_name=self.__class__.__name__)

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
        raw = payload.get("raw")
        run_id = extract_run_id(payload)
        stage = payload.get("stage")
        domain_hint = payload.get("domain_hint")

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
        
        if "url" in domain_hint:
            ENV.add_smell("url",0.0)
            stage = "material_raw"
            run_context.touch(
                run_id,
                agent="SnifferAgent",
                action="reinforcing-scent",
                reason="data-from-url",
                event="second scenting",
            )
            run_context.emit_fact(
                    run_id,
                    stage="second-scenting",
                    component="SnifferAgent",
                    result="ok",
                    reason="forwarding-to-advisor",
                    )

            domain_hint_extr = payload.get("domain_hint_extr")
            print(f"THIS IS DOMAIN HINT EXTR: {domain_hint_extr}")
            
            event_bus.emit(
                "system.smells.to.advisor",
                {   
                    "stage":stage,
                    "smells": ENV.smells,
                    "snapshots": ENV.snapshot(),
                    "raw":raw,
                    "run_id": run_id,
                    "source": payload.get("source"),
                    "domain_hint":domain_hint,
                    "domain_hint_extr":domain_hint_extr,
                }
            )
            return

        sniff(raw, agent_name=self.__class__.__name__)

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
                "domain_hint":payload.get("domain_hint")
            }
        )
    
    @on_event("system.cleaner.to.sniffer")
    def sniff_after_cleaning(self, payload:dict):
        print("THIRD RAN:",self.__class__.__name__)
        raw = payload.get("raw")
        run_id = extract_run_id(payload)
        stage = payload.get("stage")
        incoming_smells = payload.get("smells",{})

        if not raw:
            logger.error("raw not found!",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"third-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return

        if not incoming_smells:
            logger.error("smells not found",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"third-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return
        
        if payload.get("smell_context") == "post_cleaning":
            inherited_smells = payload.get("inherited_smells",{})
            new_smells = sniff(payload["raw"]["text"],agent_name=__class__.__name__)

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
        
        merged_smells = merged_smells(
            base=inherited_smells,
            new=new_smells,
            decay=0.5
        )

        ENV.reset()

        for k, v in merged_smells.items():
            ENV.add_smell(k,v)

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
                    "raw":payload["raw"],
                    "run_id": run_id,
                    "source": payload.get("source"),
                    "smell_generation":3,
                    "smell_context":"post_cleaning",
                    "merged_smells":merged_smells,

            )
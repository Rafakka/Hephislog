import json
from hephis_core.events.decorators import on_event
from hephis_core.environment import ENV
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.services.detectors.chord_detector import ChordDetector
from hephis_core.services.detectors.raw_detectors import early_advice_raw_input
from hephis_core.agents.sniffing.sniffing import extract_sniff_text, sniff
from hephis_core.utils.utils import extract_text
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
        base = base or {}
        new = new or {}
        merged = {}

        if not isinstance(base,dict):
            base = {}
        if not isinstance(new, dict):
            new = {}
        
        keys = set(base.keys()) | set(new.keys())

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

        bias = advice.get("smell_bias") or {}
        domain_hint = advice.get("domain_hint") or []

        url_stage = url_state or advice.get("url_stage")

        if "url" in domain_hint:

            for smell, weight in bias.items():
                ENV.add_smell(smell, weight)

            sniff(raw, agent_name=self.__class__.__name__)

            print(ENV.smells)

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
                    "smells": ENV.smells,
                    "domain_hint":domain_hint,
                    "origin":{
                    "type":"url",
                    "value":raw,
                    }
                }
            )
        else:
            ENV.reset()

        for smell, weight in bias.items():
            ENV.add_smell(smell, weight)

        sniff(raw, agent_name=self.__class__.__name__)

        print(ENV.smells)

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
                "source":payload.get("source"),
                "domain_hint":domain_hint,
                "raw":raw,
            }
        )

    @on_event("system.extraction.completed")
    def sniff_after_extraction(self, payload:dict):
        print("SECOND RAN:",self.__class__.__name__)
        raw = payload.get("raw")
        run_id = extract_run_id(payload)
        stage = payload.get("stage")
        domain_hint = payload.get("domain_hint")
        domain_hint_extr = payload.get("domain_hint_extr")
        smells = payload.get("smells")
        source = payload.get("source")

        print("THIS IS RAW: ",raw)

        print(smells)

        if not run_id or raw is None:
            logger.error("Dropping event without run_id or raw",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"second-sniffing",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return
        
        if stage != "material_raw":
            logger.error("Missing material_raw stage.",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"second-sniffing",
                }
            )
            return
        
        if isinstance(raw, dict) and "text" in raws:
            raw_text = raw["text"]
        elif isinstance(raw, str):
            raw_text = raw
        else:
            raw_text = None
        
        local_smells = {}

        if isinstance(raw_text, str):
            text = raw_text.lower()

            if "<li>" in text or "ingredientes" in text:
                local_smells["list_structure"] = 0.6
            
            if "chorus" in text:
                local_smells["music_structure"] = 0.7

            if "<html" in text or "</p>" in text:
                local_smells["html"] = max(local_smells.get("html",0.0),0.6)

        if isinstance(raw, dict) and source == "url":
            local_smells["url"] = max(local_smells.get("url",0.0),0.9)
        
        merged_smells = self.merged_smells(
            base=smells or {},
            new=local_smells,
            decay=0.5
        )

        run_context.touch(
            run_id,
            agent="SnifferAgent",
            action="second-sniff",
            reason="post-extraction-enrichement",
            event="second scenting",
            )
        run_context.emit_fact(
            run_id,
            stage="second-sniffing",
            component="SnifferAgent",
            result="ok",
            reason="signals-emitted",
            )

        event_bus.emit(
                "system.smells.to.advisor",
                {   
                    "stage":stage,
                    "smells":merged_smells,
                    "raw":raw,
                    "run_id": run_id,
                    "domain_hint":domain_hint,
                    "domain_hint_extr":domain_hint_extr,
                    "source":source,
                }
            )
    
    @on_event("system.cleaner.to.sniffer")
    def sniff_after_cleaning(self, payload:dict):
        print("THIRD RAN:",self.__class__.__name__)
        raw = payload.get("raw")
        run_id = extract_run_id(payload)
        stage = payload.get("stage")
        incoming_smells = payload.get("smells")

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
            new_smells = sniff(payload["raw"],agent_name=__class__.__name__)

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
        
        merged_smells = SnifferAgent.merged_smells(
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
                }
            )
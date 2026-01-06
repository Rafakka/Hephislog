import json
from hephis_core.events.decorators import on_event
from hephis_core.environment import ENV
from hephis_core.utils.logger_decorator import log_action
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context

class SnifferAgent:

    def __init__(self):
        print("INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    def sniff(self, raw):

        if not isinstance(raw, str):
            
            run_context.touch(
                run_id,
                agent="SnifferAgent",
                action="sniffed",
                domain="unknown",
                reason="file_raw_not_str",
            )

            run_context.emit_fact(
                run_id,
                stage="first-scenting",
                component="SnifferAgent",
                result="declined",
                reason="file_raw_not_str",
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
    
    @log_action(action="agt-sniffing-payload")
    @on_event("system.input_received")
    def sniff_input(self, payload: dict):

        raw = payload.get("input")
        run_id = payload.get("run_id")

        if not run_id:
            run_context.touch(
                run_id,
                agent="SnifferAgent",
                action="checking_file_id",
                reason="advicing_on_extracted_file",
                event="first scenting",
            )
            run_context.emit_fact(
                run_id,
                stage="first-scenting",
                component="SnifferAgent",
                result="declined",
                reason="not_finding_run_id",
                )
            return
        
        ENV.reset(run_id)

        self.sniff(raw)

        run_context.touch(
                run_id,
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
            "system.smells_updated",
            {
                "smells": ENV.smells,
                "snapshots": ENV.snapshot(),
                "run_id":run_id,
                "source": payload.get("source"),
                "raw":raw,
            }
        )

    @log_action(action="agt-sniffing-extracted-payload")
    @on_event("system.extraction.completed")
    def sniff_after_extraction(self, payload:dict):
        raw = payload.get("raw")
        run_id = payload.get("run_id")

        if not run_id:
            run_context.touch(
                run_id,
                agent="SnifferAgent",
                action="checking_file_id",
                reason="advicing_on_extracted_file",
                event="second scenting",
            )
            run_context.emit_fact(
                run_id,
                stage="second-scenting",
                component="SnifferAgent",
                result="declined",
                reason="not_finding_run_id",
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
                result="re_scented_file",
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
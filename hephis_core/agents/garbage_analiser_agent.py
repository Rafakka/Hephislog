from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.services.interpreters.garbage_interpreter import analyze_html_garbage
import logging



class GarbageAnaliserAgent:

    def __init__(self):
        print("* - INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.raw.fetched")
    def decide(self, payload):
        
        run_id = payload.get("run_id")
        raw_html = payload.get("raw")

        origin = payload.get("origin",{})
        url = origin.get("value")

        domain_hint= payload.get("domain_hint")

        if not run_id or not raw_html:
            logger.warning("Source file has no valid run_id or raw_url",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"analising-garbage",
                }
            )
            return
        
        if not origin or not url:
            logger.warning("Source file has missing origin or url",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"analising-garbage",
                }
            )
            return
        
        analysis = analyze_html_garbage(raw_html)

        run_context.touch(
            run_id=run_id,
            agent="GarbageAnaliserAgent",
            action="analised",
            reason="data-analised",
            event="data-flagged",
            )
        run_context.emit_fact(
            run_id,
            stage="rerouting-html-path",
            component="GabarbageAnaliserAgent",
            result="completed",
            reason="data-advised-successifully",
            )
        event_bus.emit(
                "system.garbage.analysed",
                {
                    "run_id":run_id,
                    "raw":raw_html,
                    "analysis":analysis,
                    "url_state":"resolved",
                    "domain_hint":domain_hint,
                    "origin":{
                        "type":"url",
                        "value":url,
                    },
                }
            )
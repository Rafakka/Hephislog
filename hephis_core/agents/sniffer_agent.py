import json
from hephis_core.events.decorators import on_event
from hephis_core.environment import ENV
from hephis_core.utils.logger_decorator import log_action
import hephis_core.agents.decision_agent

class SnifferAgent:

    def sniff(self, raw):
        if not isinstance(raw, str):
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
    @log_action(action="agt-sniffing-payload")
    def sniff_input(self, payload):
        raw = payload.get("input")

        ENV.smells.clear()

        self.sniff(raw)

        from hephis_core.events.event_bus import event_bus
        event_bus.emit(
            "system.smells_updated",
            {
                "smells": ENV.smells,
                "snapshots": ENV.snapshot(),
                "run_id": payload["run_id"],
                "source": payload.get("source"),
            }
        )

    @on_event("system.extraction.completed")
    @log_action(action="agt-sniffing-extracted-payload")
    def sniff_after_extraction(self, payload):
        raw = payload["raw"]
        run_id = payload["run_id"]
        self.sniff(raw)

        from hephis_core.events.event_bus import event_bus
        event_bus.emit(
        "system.smells.post.extraction",
        {
            "smells": ENV.smells,
            "snapshots": ENV.snapshot(),
            "run_id": run_id,
            "source": payload.get("source"),
            "raw":raw,
        }
    )
from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.services.cleaners.data_cleaner import clean_light_html, clean_aggressive_html
import logging


class GarbageCleanerAgent:

    def __init__(self):
        print("* - INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.garbage.analysed")
    def decide(self, payload):
        domain_hint = payload.get("domain_hint")
        origin = payload.get("origin")
        source = origin.get("value")
        analysis = payload.get("analysis")
        raw_html = payload.get("raw")
        run_id = extract_run_id(payload)

        if not run_id or not raw_html:
            logger.warning("Source file has no valid run_id or raw_url",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-garbage",
                }
            )
            return

        pre_cleaned_html = clean_light_html(raw_html)

        CLEANING_STRATEGIES = {
            "fast-path":clean_light_html,
            "heavy-path":clean_aggressive_html,
            }

        strategy = CLEANING_STRATEGIES.get(
            analysis.recommendation,
            clean_light_html
        )

        cleaned_html = strategy(pre_cleaned_html)

        run_context.touch(
            run_id=run_id,
            agent="GarbageCleanerAgent",
            action="pre-cleaned",
            reason="data-pre-cleaned",
            event="data-rerouted",
            )
        run_context.emit_fact(
            run_id,
            stage="rerouting-cleaned-html",
            component="GabarbageCleanerAgent",
            result="completed",
            reason="data-cleaned-successifully",
            )
        event_bus.emit(
                "system.external_input",
                {
                    "run_id":run_id,
                    "raw":cleaned_html,
                    "source":source,
                    "domain_hint":domain_hint,
                    "cleaning_strategy":analysis.recommendation,
                }
            )
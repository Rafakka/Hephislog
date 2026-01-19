
from hephis_core.events.decorators import on_event
from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.infra.fetchers.html_fetcher import fetch_url_as_html
import logging

logger = logging.getLogger(__name__)

class UrlFetcherAgent:
    def __init__(self):
        print("* - INIT:",self.__class__.__name__) 
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.fetch_url_input")
    def fetching_from_url(self, payload:dict):
        print("RAN:",self.__class__.__name__)
        run_id = payload.get("run_id")
        origin = payload.get("origin")
        url = origin.get("value")
        domain_hint= payload.get("domain_hint")
        smells = payload.get("smells")

        if not run_id or not url:
            logger.warning("Source file has no valid run_id or url",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"fetching-from-url",
                }
            )
            return

        raw_html = fetch_url_as_html(url)

        if not raw_html:
            run_context.touch(
                    run_id=run_id,
                    agent="UrlFetcherAgent",
                    action="declining-output-none",
                    reason="nothing-extracted",
                    event="fetching-url",
                )
            run_context.emit_fact(
                    run_id,
                    stage="fetching-url",
                    component="UrlFetcherAgent",
                    result="declined",
                    reason="nothing-extracted",
                )
            return

        run_context.touch(
            run_id=run_id,
            agent="UrlFetcherAgent",
            action="fetched",
            reason="data-fetched-from-url",
            event="data-fetched",
            )
        run_context.emit_fact(
            run_id,
            stage="fetching-url",
            component="UrlFetcherAgent",
            result="completed",
            reason="data-fetched-from-url",
            )
        event_bus.emit(
                "system.raw.fetched",
                {
                    "run_id":run_id,
                    "raw":raw_html,
                    "url_state":"resolved",
                    "smells":smells,
                    "domain_hint":domain_hint,
                    "origin":{
                        "type":"url",
                        "value":url,
                    },
                }
            )

from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
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

    @on_event("system.raw.") #fetched
    def decide(self, payload):
        run_id = payload.get("run_id")
        raw_url = payload.get("raw")

        if not run_id or not raw_url:
            logger.warning("Source file has no valid run_id or raw_url",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"analising-garbage",
                }
            )
            return
        
        data_to_keep, data_to_remove = analising_fetched_data(raw_url)


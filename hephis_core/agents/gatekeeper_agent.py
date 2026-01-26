from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

HARD_SIGNAL_DOMAIN_VETO = {
    "recipe" : {
        "chord-notation",
        "structured-music-page",
    },
    "music" : {
        "ingredient-list",
        "step-list",
    }
}

class GatekeeperAgent:

    def __init__(self):
        print("2 - INIT:",self.__class__.__name__)
        for attr_name in dir(self):
            attr = getattr(self,attr_name)
            fn = getattr(attr,"__func__", None)
            if fn and hasattr(fn,"__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)
        
    @on_event("system.external_input")
    def gatekeeper_process(self,payload):
        print("RAN:",self.__class__.__name__) 

        run_id = extract_run_id(payload)

        if not run_id:
            logger.warning("Source file has no valid id or run_id",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"reception-by-gatekeeper",
                }
            )
            return

        raw = payload.get("raw") or payload.get("cleaned_raw_v1")
        if not raw:
            logger.warning("Source file has no valid raw",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"reception-by-gatekeeper",
                }
            )
            return


        smells = payload.get("smells")
        if not smells:
            logger.warning("Source file has no valid smells",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"reception-by-gatekeeper",
                }
            )
            return
        
        print("THIS IS SMELLS: ", smells)
        
        source = payload.get("source")
        if not source:
            logger.warning("Source file has no valid source",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"reception-by-gatekeeper",
                }
            )
            return

        dominance_score = smells.dominance_score or {}
        
        if not dominance_score:
            logger.warning("Source file has no dominance_score",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"reception-by-gatekeeper",
                }
            )
            return

        vetoed_domains = {
            domain        
            for domain, hard_signals in HARD_SIGNAL_DOMAIN_VETO.items()
            if any(sig in dominance_score for sig in hard_signals)
            }
        
        if vetoed_domains: 
            logger.warning("domain vetoed by hard signal.",
            extra={
                    "agent":self.__class__.__name__,
                    "domain":domain_hint,
                    "vetoed_by":list(vetoed_domains),

                }
            )
            return {
                "allowed":False,
                "reason":"hard-signal-veto",
                "vetoed_domains":list(vetoed_domains),
            }
        
        if payload.get("domain_hint") is not None:
            logger.info("domain_hint life_cycle at gatekeeper.",
            extra={
                    "agent":self.__class__.__name__,
                    "domain":payload.get("domain_hint"),
                    "run_id":run_id,
                }
            )

        run_context.touch(
        run_id, 
        agent="GatekeeperAgent", 
        action ="received_input", 
        event="system.external_input"
        )

        run_context.emit_fact(
            run_id,
            stage="gatekeeper",
            component="GatekepperAgent",
            result="accepted",
            reason="valid_external_input"
        )

        event_bus.emit(
            "system.input_to_be_identified",
            {
                "raw":raw,
                "run_id":run_id,
                "source":source,
                "smells":smells,
                "cleaning_strategy":payload.get("cleaning_strategy"),
            },
        )
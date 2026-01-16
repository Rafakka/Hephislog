from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
import logging

logger = logging.getLogger(__name__)

HEAVY_HTML_MARKERS = [
    "<script","<style","mso-","xmlns:o",
    "xmlns:w=","<meta","<link","<!--[if"
]

CLEAN_NONE = "none"
CLEAN_LIGHT = "light"
CLEAN_HEAVY = "heavy"

class RawMaterialAdvisorAgent:

    def __init__(self):
        print("* - INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @on_event("system.smells.to.advisor")
    def decide(self, payload):
        print("RAN:",self.__class__.__name__)
        smells = payload.get("smells", {})
        run_id = extract_run_id(payload)
        raw = payload.get("raw")
        stage = payload.get("stage")
        domain_hint_extr = payload.get("domain_hint_extr",{})
        domain_hint = payload.get("domain_hint")

        if stage != "material_raw" or raw is None:
            logger.warning("payload stage or raw not found.",
            extra ={
                    "agent":self.__class__.__name__,
                    "event":"advising-cleaning",
                    "payload":list(payload.keys())
                }
            )
            return

        if not smells or not isinstance(run_id, str):
            logger.warning("payload smells or run_id not found.",
            extra ={
                    "agent":self.__class__.__name__,
                    "event":"advising-cleaning",
                    "payload":list(payload.keys())
                }
            )
            return
        
        scores = {
            "recipe":0.0,
            "music":0.0,
            "article":0.0,
        }

        if domain_hint_extr:
            scores[domain_hint_extr["value"]] += domain_hint_extr["confidence"]

        if smells.get("html", 0) > 0.6:
            scores["recipe"]+= 0.2
            scores["article"]+= 0.2
        
        if smells.get("music",0) > 0.6:
            scores["music"]+= 0.4
        
        if "<li>" in raw and "ingredientes" in raw.lower():
            scores["recipe"]+= 0.4
        
        if "chorus" in raw.lower():
            scores["music"]+= 0.5
        
        if "url" in domain_hint:
            scores.pop["local_file",None]

        best, confidence = max(scores.items(), key=lambda x:x[1])

        semantic_advice = (
            ADVISE(best, confidence)
            if confidence >= 0.6
            else ADVICE_UNCERTAIN
        )

        html_score = smells.get("html",0)
        tag_count =raw.count("<")
        lenght=len(raw)

        cleaning = CLEAN_NONE
        reason = "content appears clean"

        if any(marker in raw.lower()for marker in HEAVY_HTML_MARKERS):
            cleaning = CLEAN_HEAVY
            reason = "html boilerplate detected"

        elif html_score > 0.4 and tag_count > 50 and lenght > 2000:
            cleaning = CLEAN_LIGHT
            reason = "moderate html structure"

        if cleaning != CLEAN_NONE:
            run_context.touch(
                run_id,
                agent="rawmaterialadvisoragent",
                action="advising-cleaning-intesity",
                reason=reason,
            )
            run_context.emit_fact(
                    run_id,
                    stage="advising",
                    component="RawMaterialAdvisorAgent",
                    result="cleaning",
                    reason="raw-material-advised",
                )    

            event_bus.emit(
                "system.advisor.to.html.cleaner",
                {   
                    "run_id":run_id,
                    "stage":stage,
                    "advice" : {
                        "version":1,
                        "cleaning":cleaning,
                        "reason":reason,
                        "html_smell":html_score,
                    },
                    "raw":raw,
                    "smells":smells,
                    "source":payload.get("source"),
                    "domain_hint":payload.get("domain_hint")
                }
            )

        stage = "material_cleaned"
        
        run_context.touch(
                run_id,
                agent="rawmaterialadvisoragent",
                action="advising-cleaning-intesity",
                reason=reason,
            )
        run_context.emit_fact(
                run_id,
                stage="advising",
                component="RawMaterialAdvisorAgent",
                result="cleaning",
                reason="raw-material-advised",
            )    

        event_bus.emit(
            "system.cleaner.to.sniffer",
            {   
                "raw":raw,
                "smells":smells,
                "source":payload.get("source"),
                "run_id":run_id,
                "stage":stage,
                "html_state":"cleaned"
            }
        )
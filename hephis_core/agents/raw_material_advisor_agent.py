from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.utils.utils import extract_text, get_score
from hephis_core.contracts.advisor_to_html_cleaner import AdvisorToHtmlCleanerMessage
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
        smells = payload.get("smells")
        run_id = extract_run_id(payload)
        raw = payload.get("raw")
        stage = payload.get("stage")
        domain_hint_extr = payload.get("domain_hint_extr")
        domain_hint = payload.get("domain_hint")
        scores = payload.get("scores")

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
        
        print(smells)

        html_score = get_score(scores,"html")
        
        text = extract_text(raw)
        tag_count =text.count("<")
        lenght=len(text)

        cleaning = CLEAN_NONE
        reason = "content appears clean"

        if any(marker in text.lower()for marker in HEAVY_HTML_MARKERS):
            cleaning = CLEAN_HEAVY
            reason = "html boilerplate detected"

        elif html_score > 0.4 and tag_count > 50 and lenght > 2000:
            cleaning = CLEAN_LIGHT
            reason = "moderate html structure"

        if domain_hint_extr:
            scores[domain_hint_extr["value"]] += domain_hint_extr["confidence"]

        best, confidence = max(scores.items(), key=lambda x:x[1])

        semantic_advice = {
            "type":"confident" if confidence >= 0.6 else "uncertain",
            "value":best if confidence >= 0.6 else None,
            "confidence":confidence,
            "threshold":0.6,
            "advisor":"RawMaterialAdvisorAgent",  
            }

        if confidence < 0.6:
            semantic_type = {
                "value":"unknown",
                "confidence":confidence,
                "sources":["advisor"],
                "signals":scores,
            }
        else:
            semantic_type = {
                "value":best,
                "confidence":confidence,
                "sources":["snifer","extractor","advisor"],
                "signals":{
                    "smells":smells,
                    "domain_hint_extr":domain_hint_extr,
                    "html_score":html_score,
                }
            }

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
            
            print(semantic_advice)
            print(semantic_type)

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
                    "semantic_type":semantic_type,
                    "semantic_advice":semantic_advice,
                    "source":payload.get("source"),
                    "semantic_scores":scores,

                }
            )

        print(semantic_advice)
        print(semantic_type)

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

        msg = AdvisorToHtmlCleanerMessage.from_advisor (
            run_id=run_id,
            raw=raw,
            cleaning=cleaning,
            reason=reason,
            html_smell=html_score,
            smells=smells,
            semantic_advice=semantic_advice,
            semantic_scores=scores,
            domain_hint=payload.get("domain_hint"),
            source=payload.get("source")

        )
        event_bus.emit(
            AdvisorToHtmlCleanerMessage.EVENT,
            msg.to_event()
        )
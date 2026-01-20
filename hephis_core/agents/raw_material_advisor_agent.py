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
        source = payload.get("source")
        

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
        
        print("THIS IS RECEIVED: ",raw)

        if isinstance(raw, dict):
            text = extract_text(raw)
        elif isinstance(raw,str):
            text = raw
        else:
            logger.warning("Unsupported raw type.",
            extra ={
                    "agent":self.__class__.__name__,
                    "event":"advising-cleaning",
                    "payload":list(payload.keys())
                }
            )
            return
        
        text_lower = text.lower()
        
        lenght=len(text)
        tag_count =text.count("<")
        html_density = tag_count / max(lenght,1)

        cleaning = CLEAN_NONE
        reason = "content appears clean"

        if any(marker in text_lower for marker in HEAVY_HTML_MARKERS):
            cleaning = CLEAN_HEAVY
            reason = "html boilerplate detected"

        elif html_density > 0.5 and lenght > 2000:
            cleaning = CLEAN_HEAVY
            reason = "dense structure and large document"
        
        elif smells.get("html",0) >0.4 and tag_count >50:
            cleaning = CLEAN_LIGHT
            reason = "moderate html structure"
        
        elif domain_hint_extr and domain_hint_extr.get("source") == "extractor":
            cleaning = CLEAN_LIGHT
            reason = "content extracted from url"

        semantic_advice = {
            "type":"hint",
            "value":None,
            "confidence":0.0,
            "sources":[],
            "signals":[],
            }
        
        if domain_hint_extr:
            semantic_advice.update({
                "value":domain_hint_extr.get("value"),
                "confidence":domain_hint_extr.get("confidence",0.0),
                "sources":["extractor"],
                "signals":{
                    "domain_hint_extr":domain_hint_extr,
                },
            })
        elif domain_hint:
            semantic_advice.update({
                "value":domain_hint,
                "confidence":0.3,
                "sources":["transport"],
                "signals":{
                    "domain_hint":domain_hint,
                }
            })

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
            smells=smells,
            semantic_advice=semantic_advice,
            domain_hint=domain_hint,
            source=source,
        )
        event_bus.emit(
            AdvisorToHtmlCleanerMessage.EVENT,
            msg.to_event()
        )
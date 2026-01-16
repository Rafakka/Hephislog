from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from hephis_core.services.cleaners.data_cleaner import clean_html_artifacts
from bs4 import BeautifulSoup
import re
import logging

from hephis_core.services.cleaners.data_cleaner import (
    clean_text
)

logger = logging.getLogger(__name__)

class HtmlCleanerAgent:

    def __init__(self):
        print("* - INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    def heavy_clean_html(self, soup:BeautifulSoup) -> str:
        for tag in soup([
            "script","meta", "style","link","nonscript"]
            ):
            tag.decompose()
            text = soup.get_text(separator="")
        return clean_html_artifacts(text)
        
    def light_clean_html(self, soup:BeautifulSoup) -> str:
        text = soup.get_text(separator="")
        return clean_html_artifacts(text)

    @on_event("system.advisor.to.html.cleaner")
    def decide(self, payload):
        print("RAN:",self.__class__.__name__) 
        smells = payload.get("smells", {})
        run_id = extract_run_id(payload)
        source = payload.get("source")
        raw = payload.get("raw")
        stage = payload.get("stage")
        advice = payload.get("advice",{})

        if not run_id:
            logger.warning("run id is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"decision-making",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return
        
        if not raw:
            logger.warning("raw is missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                }
            )
            return
        
        if not smells:
            logger.warning("smells are missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                }
            )
            return
        
        if stage != "material_raw":
            logger.warning("Stage not material raw.",
            extra ={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                    "payload":list(payload.keys())
                }
            )
            return
        
        if not advice:
            logger.warning("advice not found.",
            extra ={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                    "payload":list(payload.keys())
                }
            )
            return

    
        cleaning = advice.get("cleaning","none")

        soup = BeautifulSoup(raw,"html.parser")

        if cleaning == "heavy":
            cleaned_text = self.heavy_clean_html(soup)
            reason = "heavy clean applied"
        
        elif cleaning == "light":
            cleaned_text = self.light_clean_html(soup)
            reason = "light clean applied"
        else:
            clean = soup.get_text(separator=" ")
            cleaned_text = clean_html_artifacts(clean)
            reason = "no html cleaning applied"
        

        if not cleaned_text:
            logger.warning("raw failed on cleaning",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            run_context.touch(
                run_id,
                agent="htmlcleaneragent",
                action="declined",
                reason=reason,
            )
            run_context.emit_fact(
                    run_id,
                    stage="cleaning",
                    component="HtmlCleanerAgent",
                    result="declined",
                    reason="raw-material-failed",
                )    
            return
        
        stage = "material_cleaned"

        run_context.touch(
                run_id,
                agent="htmlcleaneragent",
                action="cleaned-material",
                reason=reason,
            )
        run_context.emit_fact(
                run_id,
                stage="cleaning",
                component="HtmlCleanerAgent",
                result="completed",
                reason="raw-material-cleaned",
            )    

        event_bus.emit(
            "system.cleaner.to.sniffer",
            {   
                "raw": 
                {
                "text":clean_text,
                "format":html,
                "state":cleaned
                },
                "smells":smells,
                "source":source,
                "run_id":run_id,
                "stage":stage,
                "html_state":"cleaned"
            }
        )
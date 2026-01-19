from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.services.cleaners.data_cleaner import clean_html_artifacts
from hephis_core.contracts.advisor_to_html_cleaner import (
    AdvisorToHtmlCleanerMessage,
    HtmlCleaningAdvice,
)


from bs4 import BeautifulSoup
import re
import logging

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
        msg = AdvisorToHtmlCleanerMessage.from_event(payload)

        run_id=msg.run_id
        raw=msg.raw
        advice=msg.advice
        smells=msg.smells
        cleaning = advice.cleaning
        html_smell=advice.html_smell
        reason=advice.reason
        
        text = raw.get("text")

        if not isinstance(text,dict):
            logger.warning("HtmlCleaner received non-text raw material")
            return

        print(smells)
    
        cleaning = advice.cleaning

        soup = BeautifulSoup(text,"html.parser")

        attempted_cleaning = cleaning in ("heavy","light")

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
        
        if not attempted_cleaning and not cleaned_text:
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
        else:
            logger.debug("html cleaning skipped(not required)",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                    }
                )
        
        stage = "material_cleaned"

        print(cleaned_text)

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
                "raw":{"text":cleaned_text,
                "format":"text",
                "state":"cleaned",
                "source":msg.source,
                },
                "smells":smells,
                "smell_context":"post_cleaning",
                "run_id":run_id,
                "stage":stage,
                "html_state":"cleaned"
            }
        )
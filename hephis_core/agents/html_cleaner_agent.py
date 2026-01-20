from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.services.cleaners.data_cleaner import clean_html_artifacts
from hephis_core.utils.utils import extract_text
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
        reason=advice.reason
        
        if isinstance(raw,dict):
            logger.debug("HtmlCleaner skipping non-text raw material",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            cleaned_text = raw
            cleaning = "none"
            cleaning_applied = "none"
            reason = "non-text raw material"

        print(smells)
        
        cleaner_reason = "None"

        if cleaning in ("light","heavy"):

            text = extract_text(raw)

            soup = BeautifulSoup(text,"html.parser")

            attempted_cleaning = cleaning in ("heavy","light")

            if cleaning == "heavy":
                cleaned_text = self.heavy_clean_html(soup)
                cleaner_reason = "heavy clean applied"
            elif cleaning == "light":
                cleaned_text = self.light_clean_html(soup)
                cleaner_reason = "light clean applied"
            else:
                clean = soup.get_text(separator=" ")
                cleaned_text = clean_html_artifacts(clean)
                cleaner_reason = "no html cleaning applied"
        
            if attempted_cleaning and not cleaned_text:
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
                    reason=cleaner_reason,
                    )
                run_context.emit_fact(
                            run_id,
                            stage="cleaning",
                            component="HtmlCleanerAgent",
                            result="declined",
                            reason="raw-material-failed",
                        )    
                return

        print(cleaned_text)
        print(smells)

        inherited_smells = smells or {}

        if cleaning == "none":
            cleaned_raw = raw if isinstance(raw, dict) else {
                "text":raw,
                "format":"text",
                "state":"original",
            }
        else:
            cleaned_raw = {
                "text":cleaned_text,
                "format":"text",
                "state":"original",
            }

        run_context.touch(
                run_id,
                agent="htmlcleaneragent",
                action="cleaned-material",
                reason=cleaner_reason,
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
                "raw":cleaned_raw,
                "run_id":run_id,
                "stage":"material_cleaned",
                "smells":inherited_smells,
                "smell_context":"post_cleaning",
                "source":payload.get("source"),
            }
        )
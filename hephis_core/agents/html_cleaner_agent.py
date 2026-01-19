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
        
        if not isinstance(raw,str):
            logger.debug("HtmlCleaner skipping non-text raw material",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"cleaning-html",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            cleaned_text = raw
            cleaning_applied = "none"
            reason = "non-text raw material"

        print(smells)

        cleaner_reason = "None"

        if cleaning in ("light","heavy"):

            cleaning = advice.cleaning

            soup = BeautifulSoup(raw,"html.parser")

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
        
        stage = "material_cleaned"

        print(cleaned_text)
        print(smells)

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

        if not isinstance(raw,str):
            event_bus.emit(
            "system.cleaner.to.sniffer",
            {   
                "raw":raw,
                "smells":smells,
                "smell_context":"post_cleaning",
                "run_id":run_id,
                "stage":stage,
                "html_state":"skipped"
            }
        )
        return

        event_bus.emit(
            "system.cleaner.to.sniffer",
            {   
                "raw":{
                    "text":cleaned_text,
                    "format":"text",
                    "state":"cleaned",
                },
                "smells":smells,
                "smell_context":"post_cleaning",
                "run_id":run_id,
                "stage":stage,
                "html_state":"cleaned"
            }
        )
from hephis_core.events.bus import event_bus
from hephis_core.events.decorators import on_event
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.run_id import extract_run_id
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

def normalize_text(text:str) -> str:
    text = re.sub(r"\s+"," ", text)
    return text.strip()


class HtmlCleanerAgent:

    def __init__(self):
        print("* - INIT:", self.__class__.__name__)
        self.confidence = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            fn = getattr(attr, "__func__", None)
            if fn and hasattr(fn, "__event_name__"):
                event_bus.subscribe(fn.__event_name__, attr)

    @staticmethod
    def heavy_clean_html(raw:str) -> str:
        soup = BeautifulSoup(raw, "lxml")

        for tag in soup([
            "script","meta","link","nonscript"
        ]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        return normalize_text(text)

    @staticmethod
    def light_clean_html(raw:str) -> str:
        soup = BeautifulSoup(raw, "html.parser")

        text = soup.get_text(separator="")

        return normalize_text(text)

    @on_event("system.advisor.to.html.cleaner")
    def decide(self, payload):
        print("RAN:",self.__class__.__name__) 
        smells = payload.get("smells", {})
        run_id = extract_run_id(payload)
        source = payload.get("source")
        raw = payload["raw"]
        stage = payload.get("stage")

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
        
        if not smells:
            logger.warning("smells are missing",
            extra={
                    "agent":self.__class__.__name__,
                    "event":"decision",
                    "raw_type":type(raw).__name__,
                    "raw_is_dict":isinstance(raw, dict),
                }
            )
            return
        
        if not stage:
            logger.warning("Missing stage field.",
            extra ={
                    "agent":self.__class__.__name__,
                    "event":"decision-making",
                    "payload":list(payload.keys())
                }
            )
            return

        advice = payload.get("advice",{})
        cleaning = advice.get("cleaning","none")

        if cleaning == "heavy":
            cleaned_text = self.heavy_clean_html(raw)
        
        elif cleaning == "light":
            cleaned_text = self.light_clean_html(raw)
        else:
            cleaned_text = raw
        
        stage = "material_cleaned"

        run_context.touch(
                run_id,
                agent="htmlcleaneragent",
                action="cleaned-material",
                reason="",
            )
        run_context.emit_fact(
                run_id,
                stage="cleaning",
                component="HtmlCleanerAgent",
                result="cleaned",
                reason="raw-material-cleaned",
            )    

        event_bus.emit(
            "system.cleaner.to.sniffer",
            {   
                "run_id":run_id,
                "stage":stage,
                "raw": cleaned_text,
                "source":source,
                "html_state":"cleaned",
            }
        )
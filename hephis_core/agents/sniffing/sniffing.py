from hephis_core.environment import ENV
import logging
import json

logger = logging.getLogger(__name__)

def extract_sniff_text(raw, *, agent_name:str | None = None) -> str | None:
        if isinstance(raw, dict):
            raw_extracted = (
                raw.get("text") 
                or raw.get("lyrics") 
                or raw.get("content") 
                )
            if raw_extracted:
                return raw_extracted
        if isinstance(raw, str):
            return raw
        else:
            logger.warning("Unsupported raw type",
            extra={
                    "agent":agent_name,
                    "event":"third-sniffing",
                }
            )
            return None

def sniff(raw, *, agent_name:str | None = None) -> str | None:

        text = extract_sniff_text(raw)
        
        if not text:
            logger.warning("raw is not sniffable",
            extra={
                    "agent":agent_name,
                    "event":"first-sniffing",
                    "raw_type":type(raw),
                    "raw_is_dict":isinstance(raw,dict),
                },
            )
            return

        text = text.lower()

        if"<html" in text or "<div" in text:
            ENV.add_smell("html",0.9)
            
        if "ingrediente" in text:
            ENV.add_smell("recipe",0.6)
            
        if "modo de preparo" in text or "preparo" in text:
            ENV.add_smell("recipe",0.8)
            
        if text.strip().startswith(("{","[")):
            try:
                json.loads(text)
                ENV.add_smell("json",0.9)
            except:
                ENV.add_smell("json",0.4)

        if any(chord in text for chord in["am","em","g","c"]):
            ENV.add_smell("music",0.5)        

        if len(text) > 100_000:
            ENV.add_smell("huge_input",1.0)
    
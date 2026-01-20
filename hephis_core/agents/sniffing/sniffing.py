from hephis_core.environment import ENV
import logging
import json

logger = logging.getLogger(__name__)

def _flatten_text(value) -> list[str]:
    texts = []

    if isinstance(value,str):
        texts.append(value)
    elif isinstance(value, list):
        for item in value:
            texts.extend(_flatten_text(item))
    elif isinstance(value, dict):
        for v in value.values():
            texts.extend(_flatten_text(v))
    return texts

def extract_sniff_text(raw, *, agent_name:str | None = None) -> str | None:
    
        if isinstance(raw, str):
            return raw
        
        if isinstance(raw, dict):
            texts = _flatten_text(raw)

            if texts:
                return " ".join(texts)

            logger.warning("Dict contains no sniffable text",
                extra={
                        "agent":agent_name,
                        "event":"third-sniffing",
                    }
                )
            return None
            
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
        smells: dict[str,float] = {}

        if"<html" in text or "<div" in text:
            smells["html"] = max(smells.get("html",0),0.9)
        
        if text.strip().startswith(("{","[")):
            try:
                json.loads(text)
                smells["json"] = 0.9
            except:
                smells["json"] = 0.4
            
        if "modo de preparo" in text or "preparo" in text or "steps" in text:
            smells["recipe"] = max(smells.get("recipe",0),0.8)
        
        elif "ingrediente" in text or "ingredients" in text:
            smells["recipe"] = max(smells.get("recipe",0),0.6)
        
        elif any(chord in text for chord in["am","em","g","c"]):
            smells["music"] = 0.5

        return smells or None
    
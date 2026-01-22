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

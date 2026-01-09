import html
import requests
from typing import Optional
from hephis_core.infra.extractors.registry import extractor

@extractor(domain="*",input_type="url")
def fetch_url_as_html(url:str) -> Optional[str]:

    if not isinstance(url, str):
        return None
    
    try:                                                        
        reponse = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent":(
                    "Mozilla/5.0(X11, Linux x86_64)"
                    "AppleWebKit/537.36(KHTML, like Gecko)"
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        reponse.raise_for_status()
        return reponse.text
    except Exception as exc:
        print("FETCH FAILED", repr(exc))
        return None

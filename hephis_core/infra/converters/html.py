import html
import requests
from typing import Optional

def to_html(input_value, input_type:str) -> Optional[str]:
    if input_type == "html":
        return input_value if isinstance(input_value,str) else None

    if input_type == "url":
        return fetch_url_as_html(input_value)
    
    if input_type == "text":
        return wrap_text_as_html(input_value)

    return None

def fetch_url_as_html(url:str) -> Optional[str]:

    if not isinstance(url, str):
        return None
    
    try:                                                        
        reponse = requests.get(
            url,
            timeout=10,
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

def wrap_text_as_html(text:str)->Optional[str]:
    if not isinstance(text, str):
        return None

    escaped = html.escape(text)

    return f"""
    <html>
        <body>
            <pre>{escaped}</pre>
        </body>
    </html>
    """.strip()
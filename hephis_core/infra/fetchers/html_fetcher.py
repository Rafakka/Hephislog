import html
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent":(
                    "Mozilla/5.0(X11, Linux x86_64)"
                    "AppleWebKit/537.36(KHTML, like Gecko)"
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-language":"en-US,en;q=0.9,pt-BR;q=0.8",
}


def _fetch_with_requests(url:str) -> Optional[str]:

    try:                                                        
        requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=20,
            allow_redirects=True,
        )
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type","")
        if "text/html" not in content_type:
            logger.debug("Non-html content", extra={"url":url,"ct":content_type})
            return None

        return resp.text

    except Exception as exc:
        logger.info(
            "requests fetch failed",
            extra={"url":url,"error":repr(exc)}),
        return None

def _fetch_with_playwright(url:str) -> Optional[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright not installed")
        return None
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="domcontentloaded",
            timeout=60_000)
            page.wait_for_timeout(2_000)

            html = page.content()
            browser.close()

            return html
    except Exception as exc:
        logger.warning(
            "playwright fetch failed",
            extra={"url":url,"error":repr(exc)},
        )
        return None

def fetch_url_as_html(url:str) -> Optional[str]:
    if not isinstance(url, str) or not url.startswith("http"):
        return None
    html = _fetch_with_requests(url)
    if html:
        return html
    return _fetch_with_playwright(url)

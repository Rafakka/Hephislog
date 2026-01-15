import html
import requests
import logging
from typing import Optional
from playwright.sync_api import sync_playwright
import time
import cloudscraper


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
    with sync_playwright() as p:
        browser =p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            extra_http_headers=DEFAULT_HEADERS,
            viewport={"width":1280,"height":800},
        )
        page=context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)

        page.wait_for_function(
            """
        ()=> {
            const title = document.title || "";
            const body = document.body ? document.body.innerText: "";
            return(
                !title.toLowerCase().includes("just a moment")&&
                !body.toLowerCase()includes("checking your browser")
                );
            }
        """, 
            timeout=60_000
        )

        page.wait_for_timeout(2000)

        html = page.content()

        for _ in range(10):
            title = page.title()
            if "Just a moment" not in title:
                break
            time.sleep(1)
        
        html = page.content()

        browser.close()

        if "cdn-cgi/challenge-platform" in html:
            return None
        if len(html) < 20_000:
            return None
        return html

def _fetch_with_cloudscraper(url:str)->Optional[str]:
    try:
        scraper = cloudscraper.create_scraper(
            browser = {
                "browser":"chrome",
                "platform":"linux",
                "mobile":"False",
            }
        )
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()

        html = resp.text

        if not html or len(html) <20_000:
            logger.info(
                "cloudscraper returned short html",
                extra={"url":url, "lenght":len(html) if html else 0},
            )
            return None
        if "cf-challenge" in "html" or "Just a moment" in html:
            logger.info(
                "cloudfare challenge still present after cloudscraper",
                extra={"url":url}

            )
            return None
        return html

    except Exception as exc:
        logger.info(
            "cloudscraper failed",
            extra={"url":url, "error":(exc)},
        )
        return None

def looks_real(html:str|None)-> bool:
    if not html:
        return False
    lowered = html.lower()    
    if "just a moment" in lowered:
        return False
    if "checking your browser" in lowered:
        return False    
    if "cdn-cgi" in lowered:
        return False
    return len(html) > 20_000


def fetch_url_as_html(url:str) -> str | None:
    print("[FETCH] TRYING REQUESTS")
    html = _fetch_with_requests(url)
    if looks_real(html):
        return html
    
    print("[FETCH] TRYING CLOUDSCRAPER")
    html = _fetch_with_cloudscraper(url)
    if looks_real(html):
        return html

    print("[FETCH] TRYING PLAYWRIGHT")
    html = _fetch_with_playwright(url)
    if looks_real(html):
        return html
    
    if not html:
        print("HTML IS EMPTY")
        return None
        
    return None

# main_article.py
import requests
from readability import Document
from bs4 import BeautifulSoup
import html2text

HEADERS = {"User-Agent": "PanaceIA-WebMiner/1.0 (+mailto:you@example.com)"}

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def extract_main(html):
    doc = Document(html)              # readability
    title = doc.short_title()
    content_html = doc.summary()      # HTML of main content
    # optionally convert to markdown
    md = html2text.html2text(content_html)
    # sanitize or parse further if needed
    soup = BeautifulSoup(content_html, "lxml")
    text = soup.get_text("\n\n", strip=True)
    return {"title": title, "html": content_html, "markdown": md, "text": text}

if __name__ == "__main__":
    url = "https://www.receiteria.com.br/"
    html = fetch(url)
    out = extract_main(html)
    print("Title:", out["title"])
    print("Text preview:\n", out["text"][:800])

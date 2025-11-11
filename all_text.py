# all_text.py
import requests
from bs4 import BeautifulSoup, Comment
from bs4.element import NavigableString

HEADERS = {"User-Agent": "PanaceIA-WebMiner/1.0 (+mailto:you@example.com)"}

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def visible_text(html):
    soup = BeautifulSoup(html, "lxml")

    # remove unwanted tags
    for tag in soup(["script", "style", "noscript", "iframe", "svg", "meta", "link"]):
        tag.decompose()

    # remove comments
    for c in soup.find_all(string=lambda text: isinstance(text, Comment)):
        c.extract()

    body = soup.body or soup
    texts = []
    for elem in body.descendants:
        if isinstance(elem, NavigableString):
            t = str(elem).strip()
            if t:
                texts.append(t)
    return "\n\n".join(texts)

if __name__ == "__main__":
    url = "https://www.receiteria.com.br/"
    html = fetch(url)
    txt = visible_text(html)
    print(txt[:2000])  # preview

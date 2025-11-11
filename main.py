# requirements: requests, beautifulsoup4
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

HEADERS = {
    "User-Agent": "PanaceIA-WebMiner/1.0 (+mailto:you@example.com)"
}

def fetch(url, timeout=10):
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def parse_article(html, base_url=None):
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("h1") and soup.select_one("h1").get_text(strip=True)
    author = (soup.select_one(".author") or soup.select_one(".byline"))
    author = author.get_text(strip=True) if author else None
    content_nodes = soup.select("article p")
    content = "\n\n".join(p.get_text(strip=True) for p in content_nodes) if content_nodes else None
    date = None
    date_tag = soup.select_one("time")
    if date_tag and date_tag.has_attr("datetime"):
        date = date_tag["datetime"]
    return {"title": title, "author": author, "date": date, "content": content, "fetched_at": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    url = "https://example.com/some-article"
    html = fetch(url)
    item = parse_article(html)
    print(json.dumps(item, indent=2, ensure_ascii=False))

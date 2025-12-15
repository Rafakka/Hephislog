from bs4 import BeautifulSoup

def extract_title_from_page(soup):
    if soup.title and soup.title.string:
        raw = soup.title.string.strip()
        return raw.split("-")[0].strip()
    return "Unknown Title"


def extract_paragraphs_from_betty(html: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("div", class_="Section1")
    if not section:
        return None

    ps = section.find_all("p", class_="MsoNormal")
    if not ps:
        return None

    paragraphs = [p.get_text("\n", strip=True) for p in ps]
    title = extract_title_from_page(soup)

    return {
        "title": title,
        "text": "\n".join(paragraphs),
        "source": "betty"
    }
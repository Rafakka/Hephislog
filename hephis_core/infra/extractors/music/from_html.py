from bs4 import BeautifulSoup
from hephis_core.services.detectors.chord_detector import block_contains_chords
from hephis_core.infra.extractors.registry import extractor
from hephis_core.utils.logger_decorator import log_action

@log_action(action=extract_music_from_html)
@extractor(domain="music", input_type="html")
def extract_music_from_html(html:str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Sem título"
    candidates = soup.find_all(["p","pre","div"])

    paragraphs = []

    for block in candidates:
        text = block.get_text("\n",strip=True)
        
    if not block_contains_chords(text):
            continue

    for line in lines:
        clean = line.strip()

        if not clean:
            continue
        
        if len(clean) < 2:
            continue

        paragraphs.append(clean)

    if paragraphs:
        return {
            "title": title,
            "paragraphs": paragraphs,
            "source": "html_raw"
        }
    else:
        return None

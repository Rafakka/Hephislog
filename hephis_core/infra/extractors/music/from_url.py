from bs4 import BeautifulSoup
from hephis_core.services.cleaners.data_cleaner import normalize_url, is_url

def extract_title_from_page(soup):
    """Extracts song title from <title> tag or fallback."""
    if soup.title and soup.title.string:
        raw = soup.title.string.strip()
        return raw.split("-")[0].strip()
    return "Unknown Title"

def extract_paragraph_from_soup(soup):
    section = soup.find("div", class_="Section1")
    if section:
        ps = section.find_all("p", class_="MsoNormal")
        if ps:
            return ps

    return soup.find_all("p") or []

@log_action(action=extract_chords_and_lyrics)
def extract_music_from_url(source):

    if isinstance (source, str):
        if is_url(source):
            cleaned_url=normalize_url(source)
            page_to_scrape = requests.get(cleaned_url)
            soup = BeautifulSoup(page_to_scrape.text, "html.parser")
            paragraphs = extract_paragraph_from_soup(soup)
            title = extract_title_from_page(soup)
            return {
                    "paragraphs": paragraphs,
                    "title": title
                }
        else:
            soup = BeautifulSoup(source, 'html.parser')
            paragraphs = extract_paragraph_from_soup(soup)
            title = extract_title_from_page(soup)

            return {
                "paragraphs": paragraphs,
                "title": title
            }

    elif isinstance(source, BeautifulSoup):
        paragraphs = extract_paragraph_from_soup(source)
        title = extract_title_from_page(source)

        return {
            "paragraphs": paragraphs,
            "title": title
        }

    else:
        return {
            "paragraphs": [],
            "title": "Unknown Title"
        }
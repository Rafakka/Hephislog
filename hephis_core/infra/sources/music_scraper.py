from bs4 import BeautifulSoup
from hephis_core.services.cleaners.data_cleaner import is_url, normalize_url
import requests

## http://bettyloumusic.com/takeonme.htm

def extract_title(soup):
    if soup.title and soup.title.string:
        text = soup.title.string
        # Example: "Take On Me - Chords and Lyrics"
        return text.split("-")[0].strip()
    return "Unknown Title"

def extract_paragraph_from_soup(soup):
    section = soup.find("div", class_="Section1")
    if section:
        ps = section.find_all("p", class_="MsoNormal")
        if ps:
            return ps

    return soup.find_all("p") or []

def extract_chords_and_lyrics(source):

    if isinstance (source, str):
        if is_url(source):
            cleaned_url=normalize_url(source)
            page_to_scrape = requests.get(cleaned_url)
            soup = BeautifulSoup(page_to_scrape.text, "html.parser")
            return {
                "paragraphs": extract_paragraph_from_soup(soup),
                "title": extract_title(soup),
            }
                        
        else:
            soup = BeautifulSoup(source, 'html.parser')
            return {
                "paragraphs": extract_paragraph_from_soup(soup),
                "title": extract_title(soup),
            }

    elif isinstance (source, BeautifulSoup):
        return {
                "paragraphs": extract_paragraph_from_soup(soup),
                "title": extract_title(soup),
            }

    else:
        return []
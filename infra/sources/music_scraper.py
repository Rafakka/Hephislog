from bs4 import BeautifulSoup
from services.cleaners.data_cleaner import is_url, normalize_url
import requests

## http://bettyloumusic.com/takeonme.htm

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
            return extract_paragraph_from_soup(soup)
        else:
            soup = BeautifulSoup(source, 'html.parser')
            return extract_paragraph_from_soup(soup)

    elif isinstance (source, BeautifulSoup):
        return extract_paragraph_from_soup(source)

    else:
        return []
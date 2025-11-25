from bs4 import BeautifulSoup
import requests

## http://bettyloumusic.com/takeonme.htm

def extract_chords_and_lyrics(html):

    page_to_scrape = requests.get(html)
    print(page_to_scrape.text[:500])
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    section = soup.find("div", class_="Section1")
    paragraphs = section.find_all("p", class_="MsoNormal")

    return paragraphs
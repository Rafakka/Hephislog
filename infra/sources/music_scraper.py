from bs4 import BeautifulSoup
import requests
from utils.data_cleaner import clean_text
from services.chord_detector import looks_like_chord_line, extract_chords_from_tokens

## http://bettyloumusic.com/takeonme.htm

def extract_chords_and_lyrics(html):

    page_to_scrape = requests.get(html)
    print(page_to_scrape.text[:500])
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    section = soup.find("div", class_="Section1")
    paragraphs = section.find_all("p", class_="MsoNormal")

    pending_chords = None
    final_lines = []

    for p in paragraphs:

        cleaned_text = clean_text(p)

        chord_spans = p.find_all("span", class_="taggedChord")
        if chord_spans:
            raw_chords = [span["data-original-chord"] for span in chord_spans]
            pending_chords = [normalize_chords(ch) for ch in raw_chords]
            continue

        if looks_like_chord_line(cleaned_text):
            pending_chords = extract_chords_from_tokens(cleaned_text)
            continue

        if not cleaned_text.strip():
            if pending_chords:
                continue
            else:
                continue 

        if pending_chords:
            final_lines.append({
                "chords": pending_chords,
                "lyrics": cleaned_text
            })
            pending_chords = None

    return final_lines
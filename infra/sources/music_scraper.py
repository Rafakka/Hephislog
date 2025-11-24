from bs4 import BeautifulSoup
import requests

page_to_scrape = requests.get("http://bettyloumusic.com/takeonme.htm")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
section = soup.find("div", class_="Section1")
paragraphs = section.find_all("p", class_="MsoNormal")

pending_chords = None
final_lines = []

for p in paragraphs:

    chord_spans = p.find_all("span", class_="taggedChord")

    if chord_spans:
        raw_chords = [span["data-original-chord"] for span in chord_spans]
        pending_chords = [normalize_chords(ch) for ch in raw_chords]
        continue

    lyrics_text = clean_text(p)

    if not lyrics_text.strip():
        continue
    
    if pending_chords:
        final_lines.append({
            "chords": pending_chords,
            "lyrics": lyrics_text
        })
        pending_chords = None
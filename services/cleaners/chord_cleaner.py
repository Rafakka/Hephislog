from services.cleaners.data_cleaner import clean_text, normalize_chords
from services.detectors.chord_detector import looks_like_chord_line, extract_chords_from_tokens

def music_organizer(paragraphs):

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
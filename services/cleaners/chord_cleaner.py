
from services.cleaners.data_cleaner import clean_text, normalize_chords
from services.detectors.chord_detector import (
    looks_like_chord_line,
    extract_chords_from_tokens,
    is_chord
)

def music_organizer(paragraph_tags):
    pending_chords = None
    final_lines = []

    for p in paragraph_tags:

        cleaned_text = clean_text(p)

        if not cleaned_text.strip():
            continue

        span_chords = []
        if hasattr(p, "find_all"):
            spans = p.find_all("span", class_="taggedChord")
            for sp in spans:
                raw = sp.get("data-original-chord", "").strip()
                if raw:
                    normalized = normalize_chords(raw)
                    if is_chord(normalized):
                        span_chords.append(normalized)

        if span_chords:
            pending_chords = span_chords
            continue

        text_chords = extract_chords_from_tokens(cleaned_text)

        if text_chords:
            pending_chords = text_chords
            continue

        if pending_chords:
            final_lines.append({
                "chords": pending_chords.copy(),
                "lyrics": cleaned_text
            })
            pending_chords = None

    return final_lines

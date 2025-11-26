from services.cleaners.data_cleaner import clean_text
from services.detectors.chord_detector import is_chord, extract_chords_from_tokens
from bs4.element import NavigableString, Tag
from services.cleaners.data_cleaner import normalize_chords


def extract_chords_preserving_order(p, cleaned_text):

    chords = []

    for node in p.contents:

        # span chords
        if isinstance(node, Tag) and node.name == "span" and node.get("class") == ["taggedChord"]:
            raw = node.get("data-original-chord", "").strip()
            if raw and is_chord(raw):
                chords.append(normalize_chords(raw))

        # plaintext chords
        elif isinstance(node, NavigableString):
            text = node.strip()
            if text:
                extracted = extract_chords_from_tokens(text)
                for c in extracted:
                    chords.append(c)

    return chords



def music_organizer(paragraph_tags):

    pending_chords = None
    final_lines = []

    for p in paragraph_tags:

        cleaned = clean_text(p)
        if not cleaned:
            continue

        combined = extract_chords_preserving_order(p, cleaned)

        # is chord-line?
        if combined:
            if pending_chords:
                # merge without duplicates
                for c in combined:
                    if c not in pending_chords:
                        pending_chords.append(c)
            else:
                pending_chords = combined.copy()
            continue

        # lyric-line
        if pending_chords:
            final_lines.append({
                "chords": pending_chords.copy(),
                "lyrics": cleaned
            })
            pending_chords = None

    return final_lines
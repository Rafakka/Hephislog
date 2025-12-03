from hephis_core.services.cleaners.data_cleaner import clean_text
from hephis_core.services.detectors.chord_detector import is_chord, extract_chords_from_tokens
from bs4.element import NavigableString, Tag
from hephis_core.services.cleaners.data_cleaner import normalize_chords


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

def finalize_line(lyrics, pending_chords):
    if not pending_chords:
        return None
    return {
        "chords": pending_chords.copy(),
        "lyrics": lyrics
    }

def return_pending_chords(pending_chords, combined):
    if not combined:
        return pending_chords
    if not pending_chords:
        return combined.copy()
    else:
        new_list = pending_chords.copy()
        for c in combined:
            if c not in new_list:
                new_list.append(c)
        return new_list


def music_organizer(paragraph_tags):

    pending_chords = None
    final_lines = []

    for p in paragraph_tags:

        cleaned = clean_text(p)
        if not cleaned:
            continue

        combined = extract_chords_preserving_order(p, cleaned)

        if combined:
            pending_chords = return_pending_chords(pending_chords, combined)
            continue

        line = finalize_line(cleaned, pending_chords)
        if line:
            final_lines.append(line)
            pending_chords = None

    return final_lines
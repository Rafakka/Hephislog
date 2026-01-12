from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from hephis_core.services.cleaners.data_cleaner import clean_text
from hephis_core.services.detectors.chord_detector import ChordDetector
import re
from hephis_core.schemas.music_schemas import ChordSheetSchema

CHORD_TOKEN = r"[A-G](#|b)?(m|maj7|maj|min7|m7|dim|aug|sus2|sus4|add9|6|9|11|13)?"

def clean_duplicate_chord_blocks(text):
    """
    Removes duplicated chord blocks created by MS Word HTML.
    Example:
        'G Bm Em C G Bm Em C Take on me...' 
    becomes:
        'G Bm Em C Take on me...'
    """
    tokens = text.split()
    chords = [t for t in tokens if ChordDetector.is_main_chord(t)]

    # No chords or only one chord group? Nothing to fix
    if len(chords) < 4:
        return text

    # Detect repeating chord sequences (ABCDABCD pattern)
    mid = len(chords) // 2
    first = chords[:mid]
    second = chords[mid:mid*2]

    if first == second:
        # Remove second occurrence from the text
        cleaned = []
        skip = False
        chord_iter = iter(chords[mid:mid*2])
        next_chord = None
        try:
            next_chord = next(chord_iter)
        except StopIteration:
            next_chord = None

        for t in tokens:
            if next_chord and t == next_chord:
                # skip tokens of the duplicated block
                try:
                    next_chord = next(chord_iter)
                except StopIteration:
                    next_chord = None
                continue
            cleaned.append(t)

        return " ".join(cleaned)

    return text

def ensure_tag(obj):
    # If it's already a BeautifulSoup tag, return as is
    if isinstance(obj, Tag):
        return obj

    # If it's a list/ResultSet, pick the first valid Tag
    if isinstance(obj, (list, tuple)):
        for item in obj:
            if isinstance(item, Tag):
                return item
        # If no Tag found, wrap the whole thing
        return BeautifulSoup(f"<p>{str(obj)}</p>", "html.parser").p

    # If it's a string, parse it
    if isinstance(obj, str):
        soup = BeautifulSoup(obj, "html.parser")
        tag = soup.find("p")
        if tag:
            return tag
        return BeautifulSoup(f"<p>{obj}</p>", "html.parser").p

    # Fallback: wrap anything else
    return BeautifulSoup(f"<p>{str(obj)}</p>", "html.parser").p

def normalize_chord_line(text):
    """Normalize messy chord lines into Am D G C Bm and remove span-induced duplicates."""

    # Base cleanup
    t = re.sub(r"\s+", " ", text)
    t = t.replace("-", " ")
    t = re.sub(r"\([^)]*\)", "", t)

    # Extract all chords (including duplicated)
    chords = [m.group(0) for m in re.finditer(CHORD_TOKEN, t)]

    # Collapse span-induced duplicates WHILE preserving order
    clean = []
    seen = set()
    for c in chords:
        if not clean or clean[-1] != c:      # removes adjacent duplicates (span repetition)
            clean.append(c)

    return " ".join(clean)

def extract_inline_chords(p_tag):
    """Extract chords from <span> tags AND plaintext."""
    chords = []

    for node in p_tag.contents:

        # Tagged chords
        if isinstance(node, Tag) and node.get("class") == ["taggedChord"]:
            raw = node.get("data-original-chord", "").strip()
            if raw and is_main_chord(raw):
                chords.append(raw)

        # Plaintext chords in NavigableString
        elif isinstance(node, NavigableString):
            extracted = ChordDetector.extract_chords_from_tokens(str(node))
            chords.extend(extracted)

    return chords

def music_organizer(paragraphs):
    lines = []
    pending_chords = None

    for p in paragraphs:
        p_tag = ensure_tag(p)
        text= p_tag.get_text(separator="", strip=True)
        raw = clean_text(text)
        raw = clean_duplicate_chord_blocks(raw)

        if not raw:
            continue

        # STEP 1: Extract inline chords FIRST
        # (because this site does NOT use taggedChord spans)
        inline_chords = ChordDetector.extract_chords_from_tokens(raw.replace("-", " "))

        # PURE CHORD LINE (ex: "Am - D - G - C - Bm")
        if inline_chords and all(ChordDetector.is_main_chord(tok) for tok in raw.replace("-", " ").split()):
            # remove consecutive duplicates from span flattening
            unique = []
            for c in inline_chords:
                if not unique or unique[-1] != c:
                    unique.append(c)

            lines.append({
                "lyrics": "",
                "chords": unique.copy()
            })
            pending_chords = unique.copy()
            continue

        # MIXED LINE: lyrics + chords in same paragraph
        if inline_chords and not all(ChordDetector.is_main_chord(tok) for tok in raw.split()):
            # separate chords from lyrics
            lyric_only = raw
            for c in inline_chords:
                lyric_only = lyric_only.replace(c, "")
            lyric_only = re.sub(r'\s+', ' ', lyric_only).strip()

            lines.append({
                "lyrics": lyric_only,
                "chords": inline_chords.copy()
            })
            pending_chords = None
            continue

        # LYRIC FOLLOWING CHORD BLOCK
        if pending_chords:
            lines.append({
                "lyrics": raw,
                "chords": pending_chords.copy()
            })
            pending_chords = None
            continue

        # PURE LYRICS
        lines.append({
            "lyrics": raw,
            "chords": []
        })

    return lines

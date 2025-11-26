from schemas.music_schemas import ChordSheetSchema
from services.cleaners.data_cleaner import normalize_chords, clean_text, normalize_line
import re

ROOTS = ChordSheetSchema.ROOTS
QUALITIES = ChordSheetSchema.QUALITIES
ACCIDENTALS = ChordSheetSchema.ACCIDENTALS

_CHORD_RE = re.compile(
    r"""^
    [A-G]                # root
    (?:[#b])?            # optional accidental
    (?:                  # optional quality/extensions group
        (?:
            m|maj|maj7|m7|7|sus2|sus4|sus|dim|aug|add9|add2|
            add11|6|9|11|13|ø|°|sus4\(?\d*\)?  # common forms (extend as needed)
        )
        (?:\d*)?         # optional numbers (e.g., maj7, m7)
        (?:\([^\)]*\))?  # optional parenthesis parts like sus(2) - not typical but safe
    )?
    (?:[^\s]*)?          # allow small additional chars (e.g., "7b9") but conservative
    (?:\/[A-G](?:[#b])?)? # optional slash bass like C/G or G/B
    $""",
    re.IGNORECASE | re.VERBOSE,
)

############# HELPERS ############################

def is_root(token: str) -> bool:
    return bool(re.match(r"^[A-G](?:[#b])?$", token.strip(), re.IGNORECASE))

def is_accidental(token: str) -> bool:
    return len(token) > 1 and token[1] in ("#", "b")

def is_quality(token: str) -> bool:
    # a quick set membership test for known qualities (lowercase comparison)
    Qual = {"m","maj","maj7","m7","7","sus","sus2","sus4","dim","aug","add9","6","9","11","13","°","ø"}
    return token.strip().lower() in Qual

def is_bass(token: str) -> bool:
    return bool(re.match(r"^[A-G](?:[#b])?$", token.strip(), re.IGNORECASE))


########## MAIN FUNCTIONS #########################################

def is_main_chord(token):

    clean_token = normalize_chords(token)

    if not clean_token:
        return False

    if not is_root(clean_token[0]):
        return False

    if is_accidental(clean_token):
        remainder = clean_token[2:]
    else:
        remainder = clean_token[1:]

    if not remainder:
        return True

    if is_quality(remainder):
        return True

    return False
    
def is_chord(token: str) -> bool:
    if not token or not isinstance(token, str):
        return False
    t = token.strip()
    t = re.sub(r"\(.*\)$", "", t).strip()
    t = re.sub(r"-+$", "", t).strip()
    t = re.sub(r"[,\.\:]+$", "", t).strip()
    return bool(_CHORD_RE.match(t))

def looks_like_chord_line(text: str, min_ratio: float = 0.6) -> bool:
    if not text:
        return False
    s = re.sub(r"\(.*?\)", "", text)
    s = re.sub(r"[,\|\-]+", " ", s)
    tokens = [t for t in s.split() if t.strip()]
    if not tokens:
        return False
    chord_count = sum(1 for t in tokens if is_chord(t))
    return (chord_count / len(tokens)) >= min_ratio

def extract_chords_from_tokens(text: str) -> list[str]:
    if not text:
        return []
    s = re.sub(r"\s-\s", " ", text)
    s = re.sub(r"[,\|]+", " ", s)
    s = re.sub(r"\s{2,}", " ", s).strip()

    tokens = s.split(" ")
    final = []
    for tok in tokens:
        if not tok or tok == "-":
            continue
        tok = tok.strip()
        if re.match(r"^\(.*\)$", tok):
            continue
        if is_chord(tok):
            clean = re.sub(r"[,\-]+$", "", tok).strip()
            final.append(clean)
    return final
from hephis_core.schemas.music_schemas import ChordSheetSchema
from hephis_core.services.cleaners.data_cleaner import normalize_chords, clean_text, normalize_line
import re

ROOTS = ChordSheetSchema.ROOTS
QUALITIES = ChordSheetSchema.QUALITIES
ACCIDENTALS = ChordSheetSchema.ACCIDENTALS

_CHORD_RE = re.compile(
    r"""
    ^\s*
    [A-G]                # root
    (?:[#b])?            # accidental
    (?:                  # optional quality/extensions
        (?:
            m|maj|maj7|m7|7|sus|sus2|sus4|dim|aug|
            add9|add2|add11|6|9|11|13|°|ø
        )
        (?:\d*)?
        (?:\([^\)]*\))?
        (?:[^\s\/]*)?
    )?
    (?:\/[A-G](?:[#b])?)? # slash bass
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_PAREN_REM = re.compile(r"\([^)]*\)")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_SEP = re.compile(r"[\|,]+")

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
    t = _PAREN_REM.sub("", t).strip()
    t = re.sub(r"[,.;:\-]+$", "", t).strip()

    return bool(_CHORD_RE.match(t))

def extract_chords_from_tokens(text: str) -> list[str]:
    """
    Extract chord-like tokens from a plain line.
    """
    if not text:
        return []

    s = str(text)

    s = _PAREN_REM.sub("", s)          # remove (3x)
    s = _SEP.sub(" ", s)               # replace , | with space
    s = re.sub(r"\s*-\s*", " ", s)     # turn dashes into separators
    s = _MULTI_SPACE.sub(" ", s).strip()

    tokens = [tok.strip() for tok in s.split() if tok.strip()]

    final = []
    for tok in tokens:
        if re.fullmatch(r"[-,.;:]+", tok):
            continue
        if is_chord(tok):
            final.append(normalize_chords(tok))

    return final


def looks_like_chord_line(text: str, min_ratio: float = 0.6) -> bool:
    """
    Optional helper if you want chord detection with ratio threshold.
    """
    if not text:
        return False

    s = _PAREN_REM.sub("", text)
    s = _SEP.sub(" ", s)
    s = re.sub(r"\s*-\s*", " ", s)

    tokens = [t for t in s.split() if t.strip()]
    if not tokens:
        return False

    chord_count = sum(1 for t in tokens if is_chord(t))
    return (chord_count / len(tokens)) >= min_ratio
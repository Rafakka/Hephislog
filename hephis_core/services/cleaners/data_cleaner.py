import re
import unicodedata
from urllib.parse import urlparse, urlunparse

_MULTI_SPACE = re.compile(r"[ \t]{2,}")

_PAREN_REM = re.compile(r"\([^)]*\)")

_TRAILING_PUNCT = re.compile(r"[,.;:\-]+$")


def clean_text(text:str)-> str:
    """
    Given a BeautifulSoup tag (normally <p>), return cleaned textual content:
    - preserves normal spaces,
    - standardizes NBSPs,
    - removes multiple spaces,
    - strips at edges.
    """
    if not isinstance (text, str):
        raise TypeError(f"clean_text expected str, got {type(text)}")

    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    text = _MULTI_SPACE.sub(" ", text)
    text = text.strip()
    return text

def normalize_line(text: str) -> str:
    """
    Original project function — now extended with minimal-impact logic
    to normalize plaintext chord lines like 'Am, D, G - C (3x)'.
    """

    if not text:
        return ""

    # ↓ ORIGINAL CLEANING
    t = text.strip()

    # ↓ NEW MINIMAL PATCH — does NOT break your old behavior
    # Remove commas entirely
    t = t.replace(",", " ")

    # Normalize whitespace
    t = re.sub(r"\s+", " ", t)

    # Convert hyphens to spaces (Am - D → Am D)
    t = t.replace("-", " ")

    # Remove repetition markers (3x etc)
    t = re.sub(r"\([^)]*\)", "", t)

    # Extract chords
    matches = [m.group(0) for m in re.finditer(CHORD_TOKEN, t)]

    # If chords found → return ONLY the chords (your original logic already expected this)
    if matches:
        # Deduplicate consecutive duplicates
        cleaned = []
        for m in matches:
            if not cleaned or cleaned[-1] != m:
                cleaned.append(m)
        return " ".join(cleaned)

    # Fallback: return normalized non-chord text
    return t
    
def normalize_chords(chord: str) -> str:
    """
    Clean up an extracted chord snippet:
    - remove parentheses (3x)
    - strip whitespace
    - remove trailing punctuation
    """
    if not chord:
        return ""

    s = chord.strip()
    s = _PAREN_REM.sub("", s).strip()
    s = _TRAILING_PUNCT.sub("", s).strip()
    return s

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

def is_url(text: str) -> bool:
    if not isinstance(text, str):
        return False

    stripped = text.strip()

    result = urlparse(stripped)

    return all([result.scheme in ("http", "https"), result.netloc])

def normalize_url(text: str) -> str:
    stripped = text.strip()
    parsed = urlparse(stripped)

    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower()
    )

    return urlunparse(normalized)
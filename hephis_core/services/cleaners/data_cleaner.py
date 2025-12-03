import re
import unicodedata
from urllib.parse import urlparse, urlunparse

_MULTI_SPACE = re.compile(r"[ \t]{2,}")

_PAREN_REM = re.compile(r"\([^)]*\)")

_TRAILING_PUNCT = re.compile(r"[,.;:\-]+$")


def clean_text(tag):
    """
    Given a BeautifulSoup tag (normally <p>), return cleaned textual content:
    - preserves normal spaces,
    - standardizes NBSPs,
    - removes multiple spaces,
    - strips at edges.
    """
    if tag is None:
        return ""

    raw = tag.get_text(" ", strip=False)
    if not raw:
        return ""

    raw = raw.replace("\xa0", " ").replace("&nbsp;", " ")
    raw = _MULTI_SPACE.sub(" ", raw)
    return raw.strip()

def normalize_line(text: str) -> str:
    """
    Very light normalization for a line representing chords.
    """
    if not text:
        return ""

    s = str(text)
    s = re.sub(r"\s*-\s*", " ", s)
    s = _MULTI_SPACE.sub(" ", s)
    return s.strip()

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
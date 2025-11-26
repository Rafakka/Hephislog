import re

def clean_text(tag):
    if tag is None:
        return ""

    text = tag.get_text(" ", strip=False)
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    text = re.sub(r"[ ]{2,}", " ", text).strip()
    return text

def normalize_line(text):
    if not text:
        return ""
    text = re.sub(r"\s-\s", " ", text)
    text = re.sub(r"[ ]{3,}", "  ", text)
    return text.strip()

def normalize_chords(chord):
    if not chord:
        return ""

    chord = chord.strip()
    chord = re.sub(r"-+$", "", chord).strip()
    return chord

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")
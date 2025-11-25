import re

def clean_text(tag):
    text = tag.get_text(" ", strip=True)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_line(text):
   normalized_text = re.sub(r"-"," ",text)
   normalized_text = re.sub(r"\s+"," ", normalized_text)
   return normalized_text.strip()

def normalize_chords(chord):
    chord = re.sub(r"&nbsp;|\s+", " ", chord)
    chord = re.sub(r"-+\s*$", "", chord)
    chord = chord.strip()

    if not chord:
        return ""

    return chord[0].upper() + chord[1:]

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")
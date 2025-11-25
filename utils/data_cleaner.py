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
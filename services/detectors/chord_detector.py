from schemas.music_schemas import ChordSheetSchema
from services.cleaners.data_cleaner import normalize_chords, clean_text, normalize_line
import re

ROOTS = ChordSheetSchema.ROOTS
QUALITIES = ChordSheetSchema.QUALITIES
ACCIDENTALS = ChordSheetSchema.ACCIDENTALS

############# HELPERS ############################

def is_root(token):
    if token in ROOTS:
        return True
    else:
        return False

def is_bass(token):
    if token[0] not in ROOTS:
        return False
    if len(token) == 1:
        return True
    if len(token) == 2 and token[1] in ACCIDENTALS:
        return True
    else:
        return False

def is_accidental(token):
    if len(token) >1 and token[1] in ACCIDENTALS:
        return True
    else:
        return False

def is_quality(token):
    if token in QUALITIES:
        return True
    else:
        return False

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
    
def is_chord(token):

    clean_token = normalize_chords(token)

    if "/" in clean_token:
        parts = clean_token.split("/")
        if len(parts) != 2:
            return False
        main, bass = parts
        if is_main_chord(main) and is_bass(bass):
            return True
        else:
            return False
        
    return is_main_chord(clean_token)

def looks_like_chord_line(text):

    cleaned_text = normalize_line(text)

    tokens = cleaned_text.split()

    clean_tokens = []

    for token in tokens:
        if not token:
            continue
        if token == "-":
            continue
        clean_tokens.append(token)
    
    if not clean_tokens:
        return False
    
    for token in clean_tokens:
        if not is_chord(token):
            return False
    
    return True

def extract_chords_from_tokens(text):

    final_list = []

    cleaned_text = normalize_line(text)

    tokens = cleaned_text.split()

    for token in tokens:
        if not token:
            continue
        if token == "-":
            continue
        if token == "+":
            continue
        if is_chord(token):
            normalized = normalize_chords(token)
            final_list.append(normalized)

    return final_list
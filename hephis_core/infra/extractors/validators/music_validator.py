

def is_valid_music(raw:dict)->bool:
    if not raw:
        return False
    
    chords = raw.get("chords") or []
    lyrics = raw.get("lyrics") or []

    if not chords and not lyrics.strip():
        return False
    
    return True
    
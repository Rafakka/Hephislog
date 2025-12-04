# hephis_core/modules/music_normalizer/normalizer.py

from hephis_core.schemas.music_schemas import ChordSheetSchema


def music_normalizer(raw_lines, url=None, run_id="api"):
    """
    Normalizes raw lines from music_organizer() into a strict block format:
    
        Am D G C Bm
        Talking away...

        Am D Em C
        I'll say it anyway...
    
    Rules:
      • Chord-only lines are merged down into the next lyric line.
      • Lyric-only lines stay lyric-only.
      • If chords were inline, they stay attached.
      • No empty lines unless absolutely necessary.
    """

    normalized = []
    pending_chords = None

    for line in raw_lines:
        chords = line.get("chords", [])
        lyrics = line.get("lyrics", "").strip()

        # CASE 1 — chord-only line (store for next lyric)
        if chords and not lyrics:
            pending_chords = chords
            continue

        # CASE 2 — lyric line (may have pending chords)
        if lyrics:
            merged_chords = pending_chords if pending_chords else chords

            normalized.append({
                "lyrics": lyrics,
                "chords": merged_chords or []
            })

            pending_chords = None
            continue

        # CASE 3 — edge case: empty lyric, empty chord (ignore)
        # (dirty HTML often causes empty leftovers)
        continue

    # Now wrap into schema
    model = ChordSheetSchema(
        title="Unknown Title",
        instrument=None,
        key=None,
        sections=[
            {
                "name": "Default",
                "lines": normalized
            }
        ],
        source="scraped",
        url=url,
        run_id=run_id
    )

    return model

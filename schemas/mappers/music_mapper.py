from schemas.music_schemas import (
    ChordSheetSchema,
    ChordSectionSchema,
    ChordLineSchema
)

def map_music_data(title, extracted_data, url, source, run_id):
    return ChordSheetSchema(
        title=title,
        instrument=None,
        key=None,
        source=source,
        url=url,
        run_id=run_id,
        sections=[
            ChordSectionSchema(
                name="main",
                lines=[
                    ChordLineSchema(
                        chords=line["chords"],
                        lyrics=line["lyrics"]
                    )
                    for line in extracted_data
                ]
            )
        ]
    )
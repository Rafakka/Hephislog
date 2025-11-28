from schemas.music_schemas import ChordSheetSchema

def map_music_data(
    title: str,
    sections: list,
    source: str,
    url: str,
    run_id: str,
    instrument: str | None = None,
    key: str | None = None
):
    """
    Wrap raw organized lines into a default section, then map
    to the ChordSheetSchema (Pydantic).
    """

    wrapped_sections = [
        {
            "name": "Default",
            "lines": sections
        }
    ]

    data = {
        "title": title,
        "sections": wrapped_sections,
        "source": source,
        "url": url,
        "run_id": run_id,
        "instrument": instrument,
        "key": key
    }

    return ChordSheetSchema(**data)
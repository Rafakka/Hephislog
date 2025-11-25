from pydantic import BaseModel, StrictStr, ConfigDict
from typing import List

class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

class ChordLineSchema(BaseSchema):
    lyrics: str
    chords: List[str]


class ChordSectionSchema(BaseSchema):
    name: str
    lines: List[ChordLineSchema]

class ChordSheetSchema(BaseSchema):

    title: str
    instrument: str | None = None
    key: str | None = None
    sections: List[ChordSectionSchema]
    source:str
    url:str
    run_id:str

class ChordSheetSchema(BaseSchema):
    
    ROOTS = {"A", "B", "C", "D", "E", "F", "G"}
    QUALITIES = {
    "m", "maj", "maj7", "m7", "7", "sus", "sus2", "sus4",
    "dim", "aug", "add9", "6", "9", "11", "13", "°", "ø"}
    ACCIDENTALS = {"#", "b"}

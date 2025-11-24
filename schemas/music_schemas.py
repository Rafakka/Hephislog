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
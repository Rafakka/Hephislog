from pydantic import BaseModel, StrictStr, ConfigDict
from typing import List, ClassVar, Set
from pydantic import field_validator

class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

class ChordLineSchema(BaseSchema):
    lyrics: str
    chords: List[str]


class ChordSectionSchema(BaseSchema):
    name: str
    lines: List[ChordLineSchema]

class ChordSheetSchema(BaseSchema):

    ROOTS: ClassVar[Set[str]] = {"A", "B", "C", "D", "E", "F", "G"}

    QUALITIES: ClassVar[Set[str]] = {
        "m", "maj", "maj7", "m7", "7", "sus", "sus2", "sus4",
        "dim", "aug", "add9", "6", "9", "11", "13", "°", "ø"
    }

    ACCIDENTALS: ClassVar[Set[str]] = {"#", "b"}

    title: str
    instrument: str | None = None
    key: str | None = None
    sections: List[ChordSectionSchema]
    source: str
    url: str
    run_id: str

    @field_validator("sections", mode="before")
    @classmethod
    def must_have_sections(cls, v):
        if v is None:
            raise ValueError("sections is none(schema constrution failed)")
        if not v:
            raise ValueError("ChordSheet must contain at least one section")
        return v
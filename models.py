from pydantic import BaseModel, HttpUrl, validator
from typing import Optional
from datetime import datetime
from dateutil import parser as dateparser

class ArticleModel(BaseModel):
    url: HttpUrl
    title: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    content: Optional[str] = None

    @validator("published_date", pre=True, always=True)
    def parse_date(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        try:
            return dateparser.parse(v)
        except Exception:
            raise ValueError(f"Could not parse date: {v}")

from pydantic import BaseModel
from datetime import date

class Finding(BaseModel):
    name: str
    category: str
    source_url: str
    date_found: date
    why_it_matches_you: str


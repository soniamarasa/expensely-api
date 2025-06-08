from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    name: str
    color: Optional[str] = None

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: str

    class Config:
        from_attributes = True

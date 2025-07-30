from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    name: str
    color: Optional[str] = None

class TagCreate(TagBase):
    workspace_id: str

class Tag(TagBase):
    id: str

    class Config:
        from_attributes = True

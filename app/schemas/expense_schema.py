from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExpenseCreate(BaseModel):
    name: Optional[str]
    value: Optional[float]
    category: Optional[dict]
    tagId: Optional[str]
    date: Optional[datetime]
    userId: Optional[str]
    description: str
    color: str
    workspaceId: str


class Expense(ExpenseCreate):
    id: str
    tag: Optional[dict] = None

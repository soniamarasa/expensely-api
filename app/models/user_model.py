from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class User(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    username: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    income: Optional[float] = None

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date, datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    username: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    income: Optional[float] = None

    @field_validator("birthdate", mode="before")
    @classmethod
    def convert_datetime_to_date(cls, value):
        if isinstance(value, str):
            # Remove 'Z' final e corta tempo para 00:00:00
            if value.endswith("Z"):
                value = value[:-1]
            try:
                dt = datetime.fromisoformat(value)
                # Zera tempo
                dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                return dt.date()
            except ValueError:
                raise ValueError("Formato de data inválido")
        if isinstance(value, datetime):
            # Garante que a hora seja zero
            dt = value.replace(hour=0, minute=0, second=0, microsecond=0)
            return dt.date()
        return value


class UserOut(BaseModel):
    id: str                 
    email: EmailStr
    name: Optional[str]
    username: Optional[str]
    gender: Optional[str]
    birthdate: Optional[date]
    income: Optional[float]

    class Config:
        orm_mode = True

class PasswordChange(BaseModel):
    currentPassword: str = Field(..., min_length=6)
    newPassword: str = Field(..., min_length=6)

from pydantic import BaseModel, EmailStr

class AuthLogin(BaseModel):
    email: EmailStr
    password: str

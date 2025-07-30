from typing import List, Optional
from pydantic import BaseModel, EmailStr


class WorkspaceUser(BaseModel):
    id: str
    name: str
    email: Optional[EmailStr]

    class Config:
        orm_mode = True  # precisa para funcionar com objetos SQLAlchemy


class WorkspaceBase(BaseModel):
    name: str
    color: str
    type: str


class WorkspaceCreate(WorkspaceBase):
    users: Optional[List[str]] = []  # IDs dos usuários para associação


class WorkspaceUpdate(BaseModel):
    name: Optional[str]
    color: Optional[str]
    type: Optional[str]
    users: Optional[List[str]] = []


class Workspace(WorkspaceBase):
    id: str
    userId: str
    users: List[WorkspaceUser]

    class Config:
        orm_mode = True

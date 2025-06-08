from typing import List, Optional
from pydantic import BaseModel, EmailStr

class WorkspaceUser(BaseModel):
    id: str
    name: str
    email: Optional[EmailStr] = None


class WorkspaceCreate(BaseModel):
    name: str
    color: str
    type: str
    users: Optional[List[str]] = []


class WorkspaceUpdate(BaseModel):
    name: Optional[str]
    color: Optional[str]
    type: Optional[str]
    users: Optional[List[str]]


class Workspace(BaseModel):
    id: str
    name: str
    userId: str
    color: str
    type: str
    users: List[WorkspaceUser]

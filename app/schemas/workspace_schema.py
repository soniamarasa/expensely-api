from typing import List, Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID


class WorkspaceType(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None


class WorkspaceUser(BaseModel):
    id: UUID
    name: str
    email: Optional[EmailStr]

    class Config:
        orm_mode = True


class WorkspaceBase(BaseModel):
    name: str
    color: str
    icon: Optional[str] = None
    type: WorkspaceType


class WorkspaceCreate(WorkspaceBase):
    users: Optional[List[UUID]] = []


class WorkspaceUpdate(BaseModel):
    name: Optional[str]
    color: Optional[str]
    icon: Optional[str] = None
    type: Optional[WorkspaceType] = None
    users: Optional[List[UUID]] = []


class Workspace(WorkspaceBase):
    id: UUID
    userId: UUID
    users: List[WorkspaceUser]

    class Config:
        orm_mode = True

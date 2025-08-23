from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Workspace as WorkspaceModel, User as UserModel
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceUpdate, Workspace
from app.services import workspaces_service

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=list[Workspace])
def list_workspaces(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    workspaces = workspaces_service.list_user_workspaces(current_user, db)

    return [
        Workspace(
            id=w.id,
            name=w.name,
            userId=w.user_id,
            color=w.color,
            type=w.type,
            icon=w.icon,
            users=[{"id": u.id, "name": u.name, "email": u.email} for u in w.users],
        )
        for w in workspaces
    ]


@router.post("", response_model=Workspace, status_code=status.HTTP_201_CREATED)
def create_workspace(
    data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    workspace = workspaces_service.create_workspace(data, current_user, db)
    return workspace  # já é WorkspaceSchema


@router.put("/{workspace_id}", response_model=Workspace)
def update_workspace(
    workspace_id: str,
    data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    workspace = workspaces_service.update_workspace(
        workspace_id, data, current_user, db
    )

    return Workspace(
        id=workspace.id,
        name=workspace.name,
        userId=workspace.user_id,
        color=workspace.color,
        type=workspace.type,
        users=[{"id": u.id, "name": u.name, "email": u.email} for u in workspace.users],
    )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    workspaces_service.delete_workspace(workspace_id, current_user, db)

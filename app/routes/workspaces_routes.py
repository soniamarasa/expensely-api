from fastapi import APIRouter, Depends, HTTPException, status
from app.services import workspaces_service
from typing import List
from app.models.workspace_model import (
    WorkspaceCreate,
    WorkspaceUpdate,
    Workspace,
)

from app.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=Workspace, status_code=status.HTTP_201_CREATED)
def create_workspace(data: WorkspaceCreate, current_user=Depends(get_current_user)):
    return workspaces_service.create_workspace(data, current_user)


@router.get("/", response_model=List[Workspace])
def list_workspaces(current_user=Depends(get_current_user)):
    return workspaces_service.list_user_workspaces(current_user)


@router.put("/{workspace_id}", response_model=Workspace)
def update_workspace(
    workspace_id: str, data: WorkspaceUpdate, current_user=Depends(get_current_user)
):
    return workspaces_service.update_workspace(workspace_id, data, current_user)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: str, current_user=Depends(get_current_user)):
    workspaces_service.delete_workspace(workspace_id, current_user)
    return None

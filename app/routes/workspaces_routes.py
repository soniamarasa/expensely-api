from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
import jwt
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4

from app.config import ALGORITHM, SECRET_KEY
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
        userId=workspace.userId,
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

@router.post("/{workspace_id}/invite")
def invite_user(workspace_id: str, email: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    workspace = workspaces_service.get_workspace_by_id(workspace_id, db)
    if workspace.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Apenas o dono pode enviar convites")
    
    workspaces_service.send_workspace_invite_email(email=email, workspace_id=workspace_id, workspace_name=workspace.name, frontend_host="http://localhost:3000")
    return {"message": f"Convite enviado para {email}"}

@router.post("/accept-invite/{token}")
def accept_workspace_invite(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        workspace_id = payload.get("workspace_id")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    workspaces_service.add_user_to_workspace(user.id, workspace_id, db)
    return {"message": f"{user.email} adicionado ao workspace com sucesso"}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Workspace as WorkspaceModel, User as UserModel, workspace_users
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceUpdate, Workspace

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

# Listar todos os workspaces do usuário logado
@router.get("/", response_model=list[Workspace])
def list_workspaces(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    workspaces = db.query(WorkspaceModel)\
        .options(joinedload(WorkspaceModel.users))\
        .filter(WorkspaceModel.user_id == current_user.id).all()

    return [
        Workspace(
            id=w.id,
            name=w.name,
            userId=w.user_id,
            color=w.color,
            type=w.type,
            users=[{
                "id": u.id,
                "name": u.name,
                "email": u.email
            } for u in w.users]
        ) for w in workspaces
    ]

# Criar novo workspace
@router.post("/", response_model=Workspace, status_code=status.HTTP_201_CREATED)
def create_workspace(data: WorkspaceCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    new_workspace = WorkspaceModel(
        id=str(uuid4()),
        name=data.name,
        color=data.color,
        type=data.type,
        user_id=current_user.id
    )

    # Adiciona usuários se forem passados
    if data.users:
        users = db.query(UserModel).filter(UserModel.id.in_(data.users)).all()
        new_workspace.users.extend(users)

    db.add(new_workspace)
    db.commit()
    db.refresh(new_workspace)

    return Workspace(
        id=new_workspace.id,
        name=new_workspace.name,
        userId=new_workspace.user_id,
        color=new_workspace.color,
        type=new_workspace.type,
        users=[{
            "id": u.id,
            "name": u.name,
            "email": u.email
        } for u in new_workspace.users]
    )

# Atualizar um workspace existente
@router.put("/{workspace_id}", response_model=Workspace)
def update_workspace(workspace_id: str, data: WorkspaceUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id, user_id=current_user.id).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    if data.name:
        workspace.name = data.name
    if data.color:
        workspace.color = data.color
    if data.type:
        workspace.type = data.type
    if data.users is not None:
        users = db.query(UserModel).filter(UserModel.id.in_(data.users)).all()
        workspace.users = users  # Substitui os membros

    db.commit()
    db.refresh(workspace)

    return Workspace(
        id=workspace.id,
        name=workspace.name,
        userId=workspace.user_id,
        color=workspace.color,
        type=workspace.type,
        users=[{
            "id": u.id,
            "name": u.name,
            "email": u.email
        } for u in workspace.users]
    )

# Deletar workspace
@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id, user_id=current_user.id).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    db.delete(workspace)
    db.commit()

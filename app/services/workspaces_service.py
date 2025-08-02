from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.user_model import User as UserModel
from app.models.workspace_model import Workspace as WorkspaceModel, workspace_users
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceUpdate
from app.database import get_db

def create_workspace(data: WorkspaceCreate, current_user: UserModel, db: Session):
    workspace = WorkspaceModel(
        name=data.name, color=data.color, type=data.type, user_id=current_user.id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Criar relacionamentos (membros)
    member_ids = [current_user.id] + [
        u.id for u in data.users if u.id != current_user.id
    ]
    for uid in member_ids:
        stmt = insert(workspace_users).values(workspace_id=workspace.id, user_id=uid)
        db.execute(stmt)

    db.commit()
    return workspace


def list_user_workspaces(current_user: UserModel, db: Session):
    owned = db.query(WorkspaceModel).filter_by(user_id=current_user.id).all()

    # Para pegar os workspace_ids que o usuário participa, fazer consulta na tabela associativa:
    stmt = select(workspace_users.c.workspace_id).filter_by(user_id=current_user.id)
    joined_ids = [wid for (wid,) in db.execute(stmt).all()]

    joined = db.query(WorkspaceModel).filter(WorkspaceModel.id.in_(joined_ids)).all()

    all_workspaces = {ws.id: ws for ws in owned + joined}
    return list(all_workspaces.values())


def update_workspace(
    workspace_id: int, data: WorkspaceUpdate, current_user: UserModel, db: Session
):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    if workspace.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Apenas o dono pode editar o workspace"
        )

    for field, value in data.dict(exclude_unset=True).items():
        setattr(workspace, field, value)

    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(workspace_id: int, current_user: UserModel, db: Session):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    if workspace.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Apenas o dono pode deletar o workspace"
        )
 
    stmt = delete(workspace_users).where(workspace_users.c.workspace_id == workspace.id)
    db.execute(stmt)

    db.delete(workspace)
    db.commit()


def user_has_access_to_workspace(user_id: str, workspace_id: str, db: Session):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if workspace and workspace.user_id == user_id:
        return True

    # Consulta na tabela associativa para verificar membro:
    stmt = select(workspace_users).where(
        (workspace_users.c.workspace_id == workspace_id)
        & (workspace_users.c.user_id == user_id)
    )
    membership = db.execute(stmt).first()

    return membership is not None

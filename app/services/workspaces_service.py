from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete, select
from typing import List, Optional
from app.models.user_model import User as UserModel
from app.models.workspace_model import Workspace as WorkspaceModel, workspace_users
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceUpdate, WorkspaceUser
from app.schemas.workspace_schema import Workspace as WorkspaceSchema


def list_user_workspaces(current_user: UserModel, db: Session):
    owned = db.query(WorkspaceModel).filter_by(user_id=current_user.id).all()
    stmt = select(workspace_users.c.workspace_id).where(
        workspace_users.c.user_id == current_user.id
    )
    joined_ids = [wid for (wid,) in db.execute(stmt).all()]
    joined = db.query(WorkspaceModel).filter(WorkspaceModel.id.in_(joined_ids)).all()
    all_workspaces = {ws.id: ws for ws in owned + joined}
    return list(all_workspaces.values())


def create_workspace(data: WorkspaceCreate, current_user: UserModel, db: Session):
    # Converte type em dict JSON pronto
    type_value = dict(data.type.model_dump()) if hasattr(data.type, "model_dump") else dict(data.type.__dict__)
    type_value["id"] = str(type_value["id"])  # garante string

    workspace = WorkspaceModel(
        id=str(uuid4()), 
        name=data.name,
        color=data.color,
        icon=data.icon,
        type=type_value, 
        user_id=current_user.id,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Define membros (dono + usuários enviados)
    member_ids = [current_user.id]
    if getattr(data, "users", None):
        member_ids += [uid for uid in data.users if uid != current_user.id]

    for uid in set(member_ids):
        stmt = insert(workspace_users).values(workspace_id=workspace.id, user_id=uid)
        db.execute(stmt)
    db.commit()

    # Monta lista de usuários para o schema
    users_list: List[WorkspaceUser] = []
    for uid in set(member_ids):
        user_obj = db.query(UserModel).filter(UserModel.id == uid).first()
        if user_obj:
            users_list.append(WorkspaceUser(
                id=str(user_obj.id),
                name=user_obj.name,
                email=user_obj.email
            ))

    return WorkspaceSchema(
        id=str(workspace.id),
        userId=str(workspace.user_id),
        name=workspace.name,
        color=workspace.color,
        icon=workspace.icon,
        type=workspace.type,
        users=users_list
    )


def update_workspace(workspace_id: str, data: WorkspaceUpdate, current_user: UserModel, db: Session):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    if workspace.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Apenas o dono pode editar o workspace")

    # Atualiza campos básicos
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "users":
            continue  # usuários tratados depois
        if field == "type" and value is not None:
            type_value = value.model_dump() if hasattr(value, "model_dump") else dict(value)
            type_value["id"] = str(type_value["id"])
            setattr(workspace, field, type_value)
        else:
            setattr(workspace, field, value)

    # Atualiza membros
    if data.users is not None:
        member_ids = [current_user.id] + [uid for uid in data.users if uid != current_user.id]
        stmt = delete(workspace_users).where(workspace_users.c.workspace_id == workspace.id)
        db.execute(stmt)
        for uid in set(member_ids):
            stmt = insert(workspace_users).values(workspace_id=workspace.id, user_id=uid)
            db.execute(stmt)

    db.commit()
    db.refresh(workspace)

    # Monta lista de usuários
    users_list: List[WorkspaceUser] = []
    stmt = select(workspace_users.c.user_id).where(workspace_users.c.workspace_id == workspace.id)
    for (uid,) in db.execute(stmt).all():
        user_obj = db.query(UserModel).filter(UserModel.id == uid).first()
        if user_obj:
            users_list.append(WorkspaceUser(
                id=str(user_obj.id),
                name=user_obj.name,
                email=user_obj.email
            ))

    return WorkspaceSchema(
        id=str(workspace.id),
        userId=str(workspace.user_id),
        name=workspace.name,
        color=workspace.color,
        icon=workspace.icon,
        type=workspace.type,
        users=users_list
    )


def delete_workspace(workspace_id: str, current_user: UserModel, db: Session):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    if workspace.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Apenas o dono pode deletar o workspace")

    stmt = delete(workspace_users).where(workspace_users.c.workspace_id == workspace.id)
    db.execute(stmt)
    db.delete(workspace)
    db.commit()


def user_has_access_to_workspace(user_id: str, workspace_id: str, db: Session):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if workspace and workspace.user_id == user_id:
        return True

    stmt = select(workspace_users).where(
        (workspace_users.c.workspace_id == workspace_id)
        & (workspace_users.c.user_id == user_id)
    )
    membership = db.execute(stmt).first()
    return membership is not None

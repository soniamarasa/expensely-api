from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete, select
from typing import List, Optional
from app.models.user_model import User as UserModel
from app.models.workspace_model import Workspace as WorkspaceModel, workspace_users
from app.schemas.workspace_schema import WorkspaceCreate, WorkspaceUpdate, WorkspaceUser
from app.schemas.workspace_schema import Workspace as WorkspaceSchema
from datetime import datetime, timedelta
from jose import jwt
from app.config import SECRET_KEY, ALGORITHM, INVITE_TOKEN_EXPIRE_MINUTES, BREVO_API_KEY
import requests


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
    type_value = (
        dict(data.type.model_dump())
        if hasattr(data.type, "model_dump")
        else dict(data.type.__dict__)
    )
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
            users_list.append(
                WorkspaceUser(
                    id=str(user_obj.id), name=user_obj.name, email=user_obj.email
                )
            )

    return WorkspaceSchema(
        id=str(workspace.id),
        userId=str(workspace.user_id),
        name=workspace.name,
        color=workspace.color,
        icon=workspace.icon,
        type=workspace.type,
        users=users_list,
    )


def update_workspace(
    workspace_id: str, data: WorkspaceUpdate, current_user: UserModel, db: Session
):
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    if workspace.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Apenas o dono pode editar o workspace"
        )

    # Atualiza apenas campos básicos
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "type" and value is not None:
            type_value = (
                value.model_dump() if hasattr(value, "model_dump") else dict(value)
            )
            type_value["id"] = str(type_value.get("id", ""))
            setattr(workspace, field, type_value)
        elif field != "users":
            setattr(workspace, field, value)

    db.commit()
    db.refresh(workspace)

    # Monta lista de usuários sem alterar
    users_list: List[WorkspaceUser] = []
    stmt = select(workspace_users.c.user_id).where(
        workspace_users.c.workspace_id == workspace.id
    )
    for (uid,) in db.execute(stmt).all():
        user_obj = db.query(UserModel).filter(UserModel.id == uid).first()
        if user_obj:
            users_list.append(
                WorkspaceUser(
                    id=str(user_obj.id), name=user_obj.name, email=user_obj.email
                )
            )

    return WorkspaceSchema(
        id=str(workspace.id),
        userId=str(workspace.user_id),
        name=workspace.name,
        color=workspace.color,
        icon=workspace.icon,
        type=workspace.type,
        users=users_list,
    )


def delete_workspace(workspace_id: str, current_user: UserModel, db: Session):
    # Pegar o workspace
    workspace = db.query(WorkspaceModel).filter_by(id=workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")

    # Checar se o usuário é dono
    if workspace.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Apenas o dono pode deletar o workspace"
        )

    # Desvincular todos os usuários do workspace (limpar relacionamento many-to-many)
    workspace.users = []

    # Deletar o workspace
    db.delete(workspace)

    # Commit da transação
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


def create_workspace_invite_token(
    email: str, workspace_id: str, workspace_name: str, workspace_icon: str
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=INVITE_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "workspace_icon": workspace_icon,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def send_workspace_invite_email(
    email: str, workspace_name: str, workspace_id: str, frontend_host: str
):
    token = create_workspace_invite_token(email, workspace_id)
    invite_link = f"{frontend_host}/workspace-invite/{token}"
    payload = {
        "sender": {"name": "Expensely", "email": "soniamaradesa@gmail.com"},
        "to": [{"email": email}],
        "subject": f"Convite para workspace {workspace_name} - Expensely",
        "htmlContent": f"""
            <p>Você foi convidado para participar do workspace <b>{workspace_name}</b> no Expensely.</p>
            <p><a href="{invite_link}">Aceitar convite</a></p>
            <p>Link válido por {INVITE_TOKEN_EXPIRE_MINUTES} minutos.</p>
        """,
        "textContent": f"Link para aceitar: {invite_link}",
    }
    headers = {"api-key": BREVO_API_KEY, "Content-Type": "application/json"}
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email", json=payload, headers=headers
    )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=500, detail=f"Falha ao enviar e-mail: {response.text}"
        )


def accept_workspace_invite(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        workspace_id = payload.get("workspace_id")
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user = db.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Não existe nenhum usuário cadastrado com o e-mail {email}",
        )

    # Verifica se já é membro para não duplicar
    exists_stmt = select(workspace_users).where(
        (workspace_users.c.user_id == user.id)
        & (workspace_users.c.workspace_id == workspace_id)
    )
    if db.execute(exists_stmt).first():
        raise HTTPException(
            status_code=400, detail="Usuário já é membro deste workspace"
        )

    # Adiciona usuário ao workspace
    stmt = insert(workspace_users).values(user_id=user.id, workspace_id=workspace_id)
    db.execute(stmt)
    db.commit()

    return {"message": f"Usuário {user.email} adicionado ao workspace com sucesso"}


def add_user_to_workspace(user_id: str, workspace_id: str, db: Session):
    stmt = insert(workspace_users).values(user_id=user_id, workspace_id=workspace_id)
    db.execute(stmt)
    db.commit()

from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List
from app.models import Tag as TagModel
from app.schemas.tag_schema import TagCreate, Tag
from app.services.workspaces_service import user_has_access_to_workspace


def create_tag_service(tag: TagCreate, user_id: str, db: Session) -> Tag:
    if not user_has_access_to_workspace(user_id, tag.workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    new_tag = TagModel(
        id=str(uuid4()),
        name=tag.name,
        color=tag.color,
        user_id=user_id,
        workspace_id=tag.workspace_id, 
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return Tag.from_orm(new_tag)


def get_tags_by_workspace(workspace_id: str, user_id: str, db: Session) -> List[Tag]:
    if not user_has_access_to_workspace(user_id, workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    tags = db.query(TagModel).filter(TagModel.workspace_id == workspace_id).all()
    return [Tag.from_orm(tag) for tag in tags]


def update_tag_service(tag_id: str, tag_data: TagCreate, user_id: str, db: Session) -> Tag:
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if not tag:
        raise Exception("Tag não encontrada.")

    if not user_has_access_to_workspace(user_id, tag.workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    tag.name = tag_data.name
    tag.color = tag_data.color

    db.commit()
    db.refresh(tag)
    return Tag.from_orm(tag)


def delete_tag(tag_id: str, user_id: str, db: Session) -> dict:
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if not tag:
        raise Exception("Tag não encontrada.")

    if not user_has_access_to_workspace(user_id, tag.workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    db.delete(tag)
    db.commit()
    return {"detail": "Tag deletada com sucesso"}

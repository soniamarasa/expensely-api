from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_current_user, get_db
from app.schemas.tag_schema import TagCreate, Tag
from app.services.tags_service import (
    create_tag_service,
    get_tags_by_workspace,
    delete_tag as delete_tag_service,
    update_tag_service,
)

router = APIRouter()


@router.post("/", response_model=Tag)
def create_tag(
    tag: TagCreate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_tag_service(tag, user_id=user_data["id"], db=db)


@router.get("/{workspace_id}", response_model=List[Tag])
def list_tags(
    workspace_id: str,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_tags_by_workspace(workspace_id, user_id=user_data["id"], db=db)


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: str,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_tag_service(tag_id=tag_id, user_id=user_data["id"], db=db)


@router.put("/{tag_id}", response_model=Tag)
def update_tag(
    tag_id: str,
    tag: TagCreate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_tag_service(tag_id=tag_id, tag=tag, user_id=user_data["id"], db=db)

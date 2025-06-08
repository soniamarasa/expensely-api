from fastapi import APIRouter, Body, Depends, HTTPException
from app.services import users_service
from app.models.user_model import User
from typing import Dict

router = APIRouter()

@router.post("/user")
def create_user(user: User):
    return users_service.create_user(user.dict())

@router.get("/users")
def get_all_users():
    return users_service.get_all_users()

@router.get("/user/{user_id}")
def get_user(user_id: str):
    return users_service.get_user_by_id(user_id)

@router.put("/user/{user_id}")
def update_user(user_id: str, new_data: Dict = Body(...)):
    return users_service.update_profile(user_id, new_data)

@router.put("/user/password")
def change_password(body: Dict = Body(...)):
    access_token = body.get("access_token")
    new_password = body.get("new_password")
    if not access_token or not new_password:
        raise HTTPException(status_code=400, detail="access_token e new_password são obrigatórios")
    return users_service.update_password(access_token, new_password)

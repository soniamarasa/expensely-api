from fastapi import APIRouter
from app.models.auth_model import AuthLogin
from app.services import auth_service

router = APIRouter()

@router.post("/login")
def login(auth_data: AuthLogin):
    return auth_service.login_user(auth_data.email, auth_data.password)
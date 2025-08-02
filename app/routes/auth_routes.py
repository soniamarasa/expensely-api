from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth_model import AuthLogin
from app.services import auth_service

router = APIRouter()

@router.post("/login")
def login(auth_data: AuthLogin, db: Session = Depends(get_db)):
    return auth_service.login_user(db, auth_data.email, auth_data.password)

@router.post("/refresh-token")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, refresh_token)
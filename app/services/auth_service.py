from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.auth.jwt_handler import (
    create_access_token,
    verify_access_token,
)  # seu JWT utils
from app.models.user_model import User
from app.services.users_service import get_user_by_id, verify_password


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    access_token = create_access_token(user.id)

    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "username": user.username,
        "gender": user.gender,
        "birthdate": user.birthdate,
        "income": user.income,
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data,
    }

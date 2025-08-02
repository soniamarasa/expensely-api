from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token, 
    verify_access_token,
)
from app.config import ALGORITHM, SECRET_KEY
from app.models.user_model import User
from app.services.users_service import get_user_by_id, verify_password


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id) \

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
        "refresh_token": refresh_token, 
        "token_type": "bearer",
        "user": user_data,
    }


def refresh_access_token(db, refresh_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception

        user_id = int(payload.get("sub"))
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    from app.auth.jwt_handler import create_access_token
    new_access_token = create_access_token(user.id)

    return {"access_token": new_access_token, "token_type": "bearer"}
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.user_model import User
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
from app.config import SECRET_KEY, ALGORITHM, RESET_TOKEN_EXPIRE_MINUTES, BREVO_API_KEY
import requests
from sqlalchemy.exc import IntegrityError
from app.config import pwd_context
from app.schemas.user_schema import PasswordChange
from app.utils.hash import get_password_hash
from uuid import uuid4

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def get_all_users(db: Session):
    return db.query(User).all()


def create_user(user_data: dict):
    db: Session = SessionLocal()
    try:
        # Verifica duplicidade de email
        if db.query(User).filter(User.email == user_data["email"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este e-mail já está em uso.",
            )

        # Verifica duplicidade de username
        if (
            user_data.get("username")
            and db.query(User).filter(User.username == user_data["username"]).first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este nome de usuário já está em uso.",
            )

        # Hash da senha
        hashed_password = pwd_context.hash(user_data["password"])

        # Cria usuário com UUID
        db_user = User(
            id=str(uuid4()),
            email=user_data["email"],
            password=hashed_password,
            name=user_data.get("name"),
            username=user_data.get("username"),
            gender=user_data.get("gender"),
            birthdate=user_data.get("birthdate"),
            income=user_data.get("income"),
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        if "users_email_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este e-mail já está em uso.",
            )
        elif "users_username_key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este nome de usuário já está em uso.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Violação de integridade: dados duplicados ou inválidos.",
            )

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}",
        )

    finally:
        db.close()


def update_user(db: Session, user_id: str, update_data: dict) -> User:
    user = get_user_by_id(db, user_id)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: str, new_password: str):
    user = get_user_by_id(db, user_id)
    user.password = hash_password(new_password)
    db.commit()
    return {"message": "Senha alterada com sucesso"}


# ------------------------
# Recuperação de senha
# ------------------------
def create_password_reset_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def send_reset_email(user: User, frontend_host: str):
    token = create_password_reset_token(user)
    reset_link = f"{frontend_host}/password-reset/{token}"

    payload = {
        "sender": {"name": "Expensely", "email": "soniamaradesa@gmail.com"},
        "to": [{"email": user.email}],
        "subject": "Redefinição de senha - Expensely",
        "htmlContent": f"""
            <html>
                <body>
                    <p>Olá {user.name},</p>
                    <p>Recebemos uma solicitação para redefinir sua senha.</p>
                    <p><a href="{reset_link}">Clique aqui para redefinir sua senha</a></p>
                    <p>Esse link expira em {RESET_TOKEN_EXPIRE_MINUTES} minutos.</p>
                    <p>Se você não solicitou isso, ignore este e-mail.</p>
                    <br>
                    <p>Equipe Expensely</p>
                </body>
            </html>
        """,
        "textContent": f"Olá {user.name}, use o link para redefinir sua senha: {reset_link}. Link válido por {RESET_TOKEN_EXPIRE_MINUTES} minutos.",
    }

    headers = {"api-key": BREVO_API_KEY, "Content-Type": "application/json"}

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email", json=payload, headers=headers
    )

    if response.status_code >= 400:
        try:
            error_message = response.json()
        except Exception:
            error_message = response.text
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao enviar e-mail de recuperação: {error_message}",
        )


def update_password(db: Session, user: User, data: PasswordChange) -> User:
    if not verify_password(data.currentPassword, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta."
        )

    user.password = get_password_hash(data.newPassword)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

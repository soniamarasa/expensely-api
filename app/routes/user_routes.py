from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Dict, List
from app.database import get_db
from pytest import Session
from app.config import SECRET_KEY, ALGORITHM
from app.dependencies import get_current_user
from app.models.user_model import User
from app.schemas import UserCreate, UserOut
from app.schemas.user_schema import PasswordChange
from app.services import users_service

from fastapi import Request

router = APIRouter()

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


@router.post("/user", response_model=UserOut)
def create_user(user: UserCreate):
    return users_service.create_user(user.dict())


@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.get_all_users(db)


@router.get("/user/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.get_user_by_id(db, user_id)


@router.put("/user/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    new_data: Dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.update_user(db, user_id, new_data)


@router.put("/password/change")
def change_password(body: Dict = Body(...), db: Session = Depends(get_db)):
    access_token = body.get("access_token")
    new_password = body.get("new_password")

    if not access_token or not new_password:
        raise HTTPException(
            status_code=400, detail="access_token e new_password são obrigatórios"
        )

    # Decodifica o token para pegar o user_id
    from jose import jwt, JWTError

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    return users_service.change_password(db, user_id, new_password)


@router.post("/user/password/reset")
def send_password_reset_request(
    request_data: dict, request: Request, db: Session = Depends(get_db)
):
    user = users_service.get_user_by_email(db, request_data["email"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    frontend_host = request.headers.get("origin")  # pega o host do front

    if not frontend_host:
        raise HTTPException(status_code=400, detail="Host do frontend não informado")

    users_service.send_reset_email(user, frontend_host)
    return {"message": "E-mail de redefinição enviado com sucesso!"}


@router.put("/user/password/update", response_model=UserOut)
def update_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return users_service.update_password(db, current_user, data)


@router.get("/test-token-simple")
def test_token_simple(token: str = Depends(oauth2_scheme)):
    print("Token recebido no test-token-simple:", token)
    return {"token": token}

from fastapi import HTTPException
from datetime import date
import requests

from app.db.supabase_client import supabase


def _convert_dates_to_str(data: dict):
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()
    return data


def check_supabase_response(resp, raise_on_error=True):
    if resp is None:
        if raise_on_error:
            raise HTTPException(status_code=500, detail="Resposta do Supabase vazia")
        return None
    if hasattr(resp, "error") and resp.error:
        if raise_on_error:
            raise HTTPException(status_code=400, detail=resp.error.message)
        return None
    if hasattr(resp, "status_code") and resp.status_code >= 400:
        if raise_on_error:
            raise HTTPException(
                status_code=resp.status_code,
                detail=getattr(resp, "message", "Erro no Supabase"),
            )
        return None
    return resp.data if hasattr(resp, "data") else None


def update_user_metadata_via_rest(user_id, metadata):
    from app.db.supabase_client import SUPABASE_URL, SUPABASE_KEY

    url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"user_metadata": metadata}
    resp = requests.put(url, headers=headers, json=payload)

    if resp.status_code >= 400:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Erro ao atualizar metadata via REST: {resp.text}",
        )
    return resp.json()


def create_user(user_data):
    if not user_data.get("password"):
        raise HTTPException(status_code=400, detail="Senha é obrigatória")
    if not user_data.get("email"):
        raise HTTPException(status_code=400, detail="Email é obrigatório")

    email = user_data.get("email")
    email_check_resp = (
        supabase.table("profiles")
        .select("id")
        .eq("email", email)
        .maybe_single()
        .execute()
    )
    email_check = check_supabase_response(email_check_resp, raise_on_error=False)
    if email_check:
        raise HTTPException(status_code=409, detail="Email já está em uso")

    username = user_data.get("username")
    if username:
        username_check_resp = (
            supabase.table("profiles")
            .select("id")
            .eq("username", username)
            .maybe_single()
            .execute()
        )
        username_check = check_supabase_response(
            username_check_resp, raise_on_error=False
        )
        if username_check:
            raise HTTPException(status_code=409, detail="Esse username já está em uso")

    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": user_data["email"],
                "password": user_data["password"],
            }
        )
    except Exception as e:
        msg = str(e)
        if "email rate limit exceeded" in msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Limite de criação de usuários atingido. Tente novamente mais tarde.",
            )
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar usuário no Auth: {msg}"
        )

    if not getattr(auth_response, "user", None):
        error_msg = getattr(auth_response, "error", None)
        msg = (
            error_msg.message
            if error_msg
            else "Erro desconhecido ao criar usuário no Auth"
        )
        if (
            "User already registered" in msg
            or "already registered" in msg
            or "duplicate key" in msg
        ):
            raise HTTPException(status_code=409, detail="Email já está em uso")
        raise HTTPException(status_code=400, detail=msg)

    user_id = auth_response.user.id

    try:
        update_user_metadata_via_rest(user_id, {"display_name": user_data.get("name")})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar display_name via REST: {str(e)}"
        )

    profile_data = {
        "id": user_id,
        "name": user_data.get("name"),
        "email": email,
        "username": username,
        "gender": user_data.get("gender"),
        "birthdate": user_data.get("birthdate"),
        "income": user_data.get("income"),
    }
    profile_data = _convert_dates_to_str(profile_data)

    profile_response = supabase.table("profiles").insert(profile_data).execute()
    profile_data_resp = check_supabase_response(profile_response, raise_on_error=False)
    if profile_data_resp is None:
        detail = getattr(
            profile_response, "message", "Erro desconhecido ao inserir profile"
        )
        if "duplicate key" in detail.lower():
            raise HTTPException(status_code=409, detail="Email já está em uso")
        raise HTTPException(status_code=400, detail=detail)

    return {"message": "Usuário criado com sucesso", "user_id": user_id}


def get_all_users():
    try:
        response = supabase.table("profiles").select("*").execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado")
        return response.data
    except SupabaseException as e:
        raise HTTPException(status_code=500, detail=f"Erro Supabase: {str(e)}")


def get_user_by_id(user_id: str):
    profile_response = (
        supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    )
    if hasattr(profile_response, "error") and profile_response.error:
        raise HTTPException(status_code=404, detail=profile_response.error.message)

    user_auth_response = supabase.auth.admin.get_user_by_id(user_id)
    if hasattr(user_auth_response, "error") and user_auth_response.error:
        raise HTTPException(status_code=404, detail=user_auth_response.error.message)

    profile = profile_response.data
    profile["email"] = user_auth_response.user.email
    return profile


# Alterar dados do perfil
def update_profile(user_id, new_data):
    response = supabase.table("profiles").update(new_data).eq("id", user_id).execute()
    if hasattr(response, "error") and response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Perfil atualizado com sucesso"}


# Alterar senha (usa token do usuário)
def update_password(access_token, new_password):
    response = supabase.auth.api.update_user(access_token, {"password": new_password})
    if hasattr(response, "error") and response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Senha alterada com sucesso"}

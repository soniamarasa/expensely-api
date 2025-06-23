from fastapi import HTTPException
from app.db.supabase_client import supabase

def login_user(email: str, password: str):
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if response.user is None:
        return {'error': response.error.message if response.error else 'Email ou senha inválidos'}

    user_id = response.user.id

    profile_response = (
        supabase
        .table('profiles')
        .select('*')
        .eq('id', user_id)
        .single()
        .execute()
    )

    if hasattr(profile_response, 'error') and profile_response.error:
        raise HTTPException(status_code=404, detail=f"Perfil não encontrado para o usuário {user_id}")

    profile_data = profile_response.data

   
    user_data = {
        'id': user_id,
        'email': response.user.email,
        **profile_data 
    }

    return {
        'access_token': response.session.access_token,
        'refresh_token': response.session.refresh_token,
        'user': user_data
    }

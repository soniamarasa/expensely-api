from app.db.supabase_client import supabase

def login_user(email: str, password: str):
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if response.user is None:
        return {'error': response.error.message if response.error else 'Email ou senha inválidos'}

    return {
        'message': 'Login bem-sucedido',
        'access_token': response.session.access_token,
        'refresh_token': response.session.refresh_token,
        'user': {
            'id': response.user.id,
            'email': response.user.email
        }
    }

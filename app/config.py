import os
from dotenv import load_dotenv
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", 60))

# Brevo (Email)
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

# Frontend (URL base para links como reset de senha)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Segurança mínima: validações
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não está definida no .env")
if not BREVO_API_KEY:
    raise ValueError("BREVO_API_KEY não está definida no .env")

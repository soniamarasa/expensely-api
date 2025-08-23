import os
from dotenv import load_dotenv
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
INVITE_TOKEN_EXPIRE_MINUTES = int(os.getenv("INVITE_TOKEN_EXPIRE_MINUTES", 60 * 5))
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY não está definida no .env")
if not BREVO_API_KEY:
    raise ValueError("BREVO_API_KEY não está definida no .env")

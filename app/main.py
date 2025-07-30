from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa suas rotas organizadas por domínio
from app.routes import (
    user_routes,
    auth_routes,
    workspaces_routes,
    expenses_routes,
    tags_routes,
)

app = FastAPI(
    title="Expensely API",
    version="1.0.0",
    description="Backend da aplicação Expensely com autenticação JWT e PostgreSQL.",
)

# CORS - ajuste conforme necessário
origins = [
    "http://localhost:5173",  # Front-end local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluindo as rotas
app.include_router(auth_routes.router, prefix="/api", tags=["Auth"])
app.include_router(user_routes.router, prefix="/api", tags=["Usuários"])
app.include_router(
    workspaces_routes.router, prefix="/api/workspaces", tags=["Workspaces"]
)
app.include_router(expenses_routes.router, prefix="/api/expenses", tags=["Despesas"])
app.include_router(tags_routes.router, prefix="/api/tags", tags=["Tags"])

# Endpoint raiz
@app.get("/")
def root():
    return {"message": "Expensely API is running 🎯"}

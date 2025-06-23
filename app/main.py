from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  

from app.routes import (
    user_routes,
    auth_routes,
    workspaces_routes,
    expenses_routes,
    tags_routes,
)

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_routes.router, prefix="/api", tags=["Usuários"])
app.include_router(auth_routes.router, prefix="/api", tags=["Auth"])
app.include_router(
    workspaces_routes.router, prefix="/api/workspaces", tags=["Workspaces"]
)
app.include_router(expenses_routes.router, prefix="/expenses", tags=["expenses"])
app.include_router(tags_routes.router, prefix="/tags", tags=["tags"])


@app.get("/")
def root():
    return {"message": "Expensely API is running"}

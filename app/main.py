from fastapi import FastAPI
from app.routes import user_routes, auth_routes

app = FastAPI()

app.include_router(user_routes.router, prefix="/api", tags=["Usuários"])
app.include_router(auth_routes.router, prefix="/api", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "Expensely API is running"}
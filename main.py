from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.routers import control_diferencias

load_dotenv()

app = FastAPI(
    title="Control de Diferencias Financieras",
    description="API para analizar y comparar datos financieros de diferentes fuentes.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(control_diferencias.router,
                   prefix="/posiciones", tags=["Control de Diferencias"])

@app.get("/", tags=["Inicio"])
def read_root():
    return {
        "mensaje": "Bienvenido al servidor de Control de Diferencias Financieras",
    }

if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", 8000))

    uvicorn.run("main:app", host=host, port=port, reload=True)

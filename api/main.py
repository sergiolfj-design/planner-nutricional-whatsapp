from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Importar a app do backend
from backend.main import app

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "online", "service": "Planner Nutricional API"}
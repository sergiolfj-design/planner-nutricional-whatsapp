"""
Rotas de Planner Mensal
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.models import Nutricionista
from app.database import SessionLocal
from app.routes.nutricionista_routes import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rotas em desenvolvimento - será completado na Fase 2
@router.post("/")
async def criar_planner():
    """Criar novo planner mensal - EM DESENVOLVIMENTO"""
    return {"message": "Endpoint em desenvolvimento"}

@router.get("/{planner_id}")
async def obter_planner(planner_id: int):
    """Obter planner - EM DESENVOLVIMENTO"""
    return {"message": "Endpoint em desenvolvimento"}

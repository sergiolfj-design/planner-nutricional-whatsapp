"""
Rotas de Dashboard e Relatórios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import Optional

from app.schemas import DashboardResponse
from app.models import Nutricionista, PlannerMensal, Dashboard, Paciente
from app.services.dashboard_service import dashboard_service
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

# ==================== GERAR DASHBOARD ====================

@router.post("/{planner_id}", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def gerar_dashboard(
    planner_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gerar ou atualizar dashboard para um planner
    """
    try:
        planner = db.query(PlannerMensal).filter(
            PlannerMensal.id_planner_mensal == planner_id,
            PlannerMensal.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not planner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planner não encontrado",
            )
        
        resultado = dashboard_service.gerar_dashboard(db, planner_id)
        
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao gerar dashboard",
            )
        
        logger.info(f"✅ Dashboard gerado para planner {planner_id}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar dashboard",
        )

# ==================== OBTER DASHBOARD ====================

@router.get("/{planner_id}")
async def obter_dashboard(
    planner_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter dashboard de um planner
    """
    try:
        planner = db.query(PlannerMensal).filter(
            PlannerMensal.id_planner_mensal == planner_id,
            PlannerMensal.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not planner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planner não encontrado",
            )
        
        dashboard = db.query(Dashboard).filter(
            Dashboard.id_planner_mensal == planner_id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard não foi gerado para este planner",
            )
        
        return dashboard
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter dashboard",
        )

# ==================== EXPORTAR PDF ====================

@router.post("/{planner_id}/exportar-pdf")
async def exportar_dashboard_pdf(
    planner_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exportar dashboard como PDF
    """
    try:
        planner = db.query(PlannerMensal).filter(
            PlannerMensal.id_planner_mensal == planner_id,
            PlannerMensal.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not planner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planner não encontrado",
            )
        
        logger.info(f"📄 Gerando PDF para planner {planner_id}")
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Funcionalidade de exportação PDF em desenvolvimento",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao exportar PDF",
        )
"""
Rotas de Gerenciamento de Pacientes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import logging
from datetime import datetime

from app.schemas import (
    PacienteCadastro, PacienteResponse, PacienteUpdate
)
from app.models import Nutricionista, Paciente
from app.database import SessionLocal
from app.routes.nutricionista_routes import get_current_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== CRIAR PACIENTE ====================

@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def criar_paciente(
    dados: PacienteCadastro,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar novo paciente
    
    Apenas nutricionista autenticada pode criar pacientes para ela mesma.
    
    Args:
        dados: Dados do paciente
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        PacienteResponse com dados do novo paciente
        
    Raises:
        HTTPException 400 se WhatsApp já cadastrado
    """
    try:
        # Validar se WhatsApp já existe para essa nutricionista
        existente = db.query(Paciente).filter(
            Paciente.whatsapp == dados.whatsapp,
            Paciente.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este WhatsApp já está cadastrado para sua conta",
            )
        
        # Criar novo paciente
        paciente = Paciente(
            id_nutricionista=current_user.id_nutricionista,
            nome=dados.nome,
            whatsapp=dados.whatsapp,
            data_nascimento=dados.data_nascimento,
            objetivo_principal=dados.objetivo_principal,
            observacoes=dados.observacoes,
            ativo=True,
            data_criacao=datetime.utcnow()
        )
        
        db.add(paciente)
        db.commit()
        db.refresh(paciente)
        
        logger.info(f"✅ Paciente criado: {paciente.nome} ({paciente.whatsapp})")
        
        return paciente
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar paciente",
        )

# ==================== LISTAR PACIENTES ====================

@router.get("/", response_model=List[PacienteResponse])
async def listar_pacientes(
    ativo: bool = Query(None, description="Filtrar por status ativo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar pacientes da nutricionista autenticada
    
    Suporta paginação e filtros.
    
    Args:
        ativo: Filtrar apenas ativos/inativos
        skip: Número de registros para pular
        limit: Limite de registros a retornar
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        Lista de PacienteResponse
    """
    try:
        query = db.query(Paciente).filter(
            Paciente.id_nutricionista == current_user.id_nutricionista
        )
        
        if ativo is not None:
            query = query.filter(Paciente.ativo == ativo)
        
        pacientes = query.order_by(
            desc(Paciente.data_criacao)
        ).offset(skip).limit(limit).all()
        
        return pacientes
        
    except Exception as e:
        logger.error(f"Erro ao listar pacientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar pacientes",
        )

# ==================== OBTER PACIENTE ====================

@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obter_paciente(
    paciente_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter informações de um paciente específico
    
    Args:
        paciente_id: ID do paciente
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        PacienteResponse
        
    Raises:
        HTTPException 404 se não encontrado
        HTTPException 403 se não pertence à nutricionista
    """
    try:
        paciente = db.query(Paciente).filter(
            Paciente.id_paciente == paciente_id,
            Paciente.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado",
            )
        
        return paciente
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter paciente",
        )

# ==================== ATUALIZAR PACIENTE ====================

@router.put("/{paciente_id}", response_model=PacienteResponse)
async def atualizar_paciente(
    paciente_id: int,
    dados: PacienteUpdate,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar informações de um paciente
    
    Args:
        paciente_id: ID do paciente
        dados: Dados para atualizar
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        PacienteResponse atualizado
        
    Raises:
        HTTPException 404 se não encontrado
    """
    try:
        paciente = db.query(Paciente).filter(
            Paciente.id_paciente == paciente_id,
            Paciente.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado",
            )
        
        # Atualizar apenas campos fornecidos
        if dados.nome:
            paciente.nome = dados.nome
        if dados.whatsapp:
            paciente.whatsapp = dados.whatsapp
        if dados.objetivo_principal:
            paciente.objetivo_principal = dados.objetivo_principal
        if dados.observacoes is not None:
            paciente.observacoes = dados.observacoes
        if dados.ativo is not None:
            paciente.ativo = dados.ativo
        
        paciente.data_atualizacao = datetime.utcnow()
        
        db.commit()
        db.refresh(paciente)
        
        logger.info(f"✅ Paciente atualizado: {paciente.nome}")
        
        return paciente
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar paciente",
        )

# ==================== DESATIVAR PACIENTE ====================

@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desativar_paciente(
    paciente_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Desativar um paciente (soft delete)
    
    Args:
        paciente_id: ID do paciente
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Raises:
        HTTPException 404 se não encontrado
    """
    try:
        paciente = db.query(Paciente).filter(
            Paciente.id_paciente == paciente_id,
            Paciente.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado",
            )
        
        paciente.ativo = False
        paciente.data_atualizacao = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"✅ Paciente desativado: {paciente.nome}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao desativar paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desativar paciente",
        )

# ==================== BUSCAR POR WHATSAPP ====================

@router.get("/whatsapp/{whatsapp_number}", response_model=PacienteResponse)
async def obter_paciente_por_whatsapp(
    whatsapp_number: str,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter paciente por número de WhatsApp
    
    Args:
        whatsapp_number: Número do WhatsApp
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        PacienteResponse
        
    Raises:
        HTTPException 404 se não encontrado
    """
    try:
        paciente = db.query(Paciente).filter(
            Paciente.whatsapp == whatsapp_number,
            Paciente.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado",
            )
        
        return paciente
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar paciente por WhatsApp: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar paciente",
        )

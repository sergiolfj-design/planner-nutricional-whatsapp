"""
Rotas de Gerenciamento de Metas Nutricionais
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import logging
from datetime import datetime

from app.schemas import MetaCadastro, MetaResponse
from app.models import Nutricionista, Meta, MetaPaciente, Paciente
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

# ==================== CRIAR META ====================

@router.post("/", response_model=MetaResponse, status_code=status.HTTP_201_CREATED)
async def criar_meta(
    dados: MetaCadastro,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova meta para a nutricionista
    
    Args:
        dados: Dados da meta
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        MetaResponse com dados da meta criada
    """
    try:
        meta = Meta(
            id_nutricionista=current_user.id_nutricionista,
            nome=dados.nome,
            descricao=dados.descricao,
            ativa=dados.ativa,
            data_criacao=datetime.utcnow()
        )
        
        db.add(meta)
        db.commit()
        db.refresh(meta)
        
        logger.info(f"✅ Meta criada: {meta.nome}")
        
        return meta
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar meta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar meta",
        )

# ==================== LISTAR METAS ====================

@router.get("/", response_model=List[MetaResponse])
async def listar_metas(
    ativa: bool = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar metas da nutricionista autenticada
    
    Args:
        ativa: Filtrar por status ativo
        skip: Paginação
        limit: Limite de registros
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        Lista de MetaResponse
    """
    try:
        query = db.query(Meta).filter(
            Meta.id_nutricionista == current_user.id_nutricionista
        )
        
        if ativa is not None:
            query = query.filter(Meta.ativa == ativa)
        
        metas = query.order_by(
            desc(Meta.data_criacao)
        ).offset(skip).limit(limit).all()
        
        return metas
        
    except Exception as e:
        logger.error(f"Erro ao listar metas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar metas",
        )

# ==================== OBTER META ====================

@router.get("/{meta_id}", response_model=MetaResponse)
async def obter_meta(
    meta_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter informações de uma meta específica
    
    Args:
        meta_id: ID da meta
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        MetaResponse
        
    Raises:
        HTTPException 404 se não encontrado
    """
    try:
        meta = db.query(Meta).filter(
            Meta.id_meta == meta_id,
            Meta.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta não encontrada",
            )
        
        return meta
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter meta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter meta",
        )

# ==================== ATUALIZAR META ====================

@router.put("/{meta_id}", response_model=MetaResponse)
async def atualizar_meta(
    meta_id: int,
    dados: MetaCadastro,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar informações de uma meta
    
    Args:
        meta_id: ID da meta
        dados: Dados para atualizar
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        MetaResponse atualizado
    """
    try:
        meta = db.query(Meta).filter(
            Meta.id_meta == meta_id,
            Meta.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta não encontrada",
            )
        
        meta.nome = dados.nome
        meta.descricao = dados.descricao
        meta.ativa = dados.ativa
        
        db.commit()
        db.refresh(meta)
        
        logger.info(f"✅ Meta atualizada: {meta.nome}")
        
        return meta
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar meta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar meta",
        )

# ==================== DELETAR META ====================

@router.delete("/{meta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_meta(
    meta_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletar uma meta
    
    Nota: Apenas deleta se não estiver vinculada a pacientes
    
    Args:
        meta_id: ID da meta
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Raises:
        HTTPException 404 se não encontrado
        HTTPException 400 se vinculada a pacientes
    """
    try:
        meta = db.query(Meta).filter(
            Meta.id_meta == meta_id,
            Meta.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta não encontrada",
            )
        
        # Verificar se há pacientes com essa meta
        vinculo = db.query(MetaPaciente).filter(
            MetaPaciente.id_meta == meta_id
        ).first()
        
        if vinculo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meta não pode ser deletada pois está vinculada a pacientes",
            )
        
        db.delete(meta)
        db.commit()
        
        logger.info(f"✅ Meta deletada: {meta.nome}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar meta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar meta",
        )

# ==================== ASSOCIAR META A PACIENTE ====================

@router.post("/{meta_id}/associar-paciente/{paciente_id}", status_code=status.HTTP_201_CREATED)
async def associar_meta_paciente(
    meta_id: int,
    paciente_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Associar uma meta a um paciente
    
    Args:
        meta_id: ID da meta
        paciente_id: ID do paciente
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException 404 se meta ou paciente não encontrado
        HTTPException 400 se já associado
    """
    try:
        # Verificar se meta pertence à nutricionista
        meta = db.query(Meta).filter(
            Meta.id_meta == meta_id,
            Meta.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta não encontrada",
            )
        
        # Verificar se paciente pertence à nutricionista
        paciente = db.query(Paciente).filter(
            Paciente.id_paciente == paciente_id,
            Paciente.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado",
            )
        
        # Verificar se já está associado
        existente = db.query(MetaPaciente).filter(
            MetaPaciente.id_meta == meta_id,
            MetaPaciente.id_paciente == paciente_id
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meta já está associada a este paciente",
            )
        
        # Criar associação
        meta_paciente = MetaPaciente(
            id_paciente=paciente_id,
            id_meta=meta_id,
            ativa=True,
            data_vinculo=datetime.utcnow()
        )
        
        db.add(meta_paciente)
        db.commit()
        
        logger.info(f"✅ Meta {meta.nome} associada ao paciente {paciente.nome}")
        
        return {"message": f"Meta '{meta.nome}' associada ao paciente '{paciente.nome}'"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao associar meta a paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao associar meta",
        )

# ==================== DESASSOCIAR META DO PACIENTE ====================

@router.delete("/{meta_id}/desassociar-paciente/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desassociar_meta_paciente(
    meta_id: int,
    paciente_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remover associação de meta com paciente
    
    Args:
        meta_id: ID da meta
        paciente_id: ID do paciente
        current_user: Nutricionista autenticada
        db: Sessão do banco
    """
    try:
        # Verificar propriedade
        meta = db.query(Meta).filter(
            Meta.id_meta == meta_id,
            Meta.id_nutricionista == current_user.id_nutricionista
        ).first()
        
        if not meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta não encontrada",
            )
        
        # Buscar associação
        meta_paciente = db.query(MetaPaciente).filter(
            MetaPaciente.id_meta == meta_id,
            MetaPaciente.id_paciente == paciente_id
        ).first()
        
        if not meta_paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associação não encontrada",
            )
        
        db.delete(meta_paciente)
        db.commit()
        
        logger.info(f"✅ Associação removida: Meta {meta.nome} - Paciente {paciente_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao desassociar meta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desassociar meta",
        )

"""
Rotas de Autenticação e Nutricionista
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi import Header
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.schemas import (
    NutricionistaCadastro, NutricionistaResponse, 
    NutricionistaUpdate, LoginRequest, TokenResponse, 
    TokenRefreshRequest
)
from app.services.auth_service import auth_service
from app.database import SessionLocal
from app.models import Nutricionista
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== DEPENDENCY ====================

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> Nutricionista:
    """
    Dependency para validar token e retornar usuário atual
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Remover "Bearer " do início
    try:
        token = authorization.replace("Bearer ", "")
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decodificar token
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extrair email do payload
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar nutricionista no banco
    nutricionista = db.query(Nutricionista).filter(
        Nutricionista.email == email,
        Nutricionista.ativo == True
    ).first()
    
    if not nutricionista:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nutricionista não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return nutricionista
# ==================== ROTAS DE AUTENTICAÇÃO ====================

@router.post("/login", response_model=TokenResponse, tags=["Autenticação"])
async def login(
    credenciais: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login da nutricionista
    
    Retorna access_token e refresh_token para autenticação
    
    Args:
        credenciais: Email e senha
        db: Sessão do banco
        
    Returns:
        TokenResponse com tokens
        
    Raises:
        HTTPException 401 se credenciais inválidas
    """
    # Autenticar nutricionista
    nutricionista = auth_service.autenticar_nutricionista(
        db, credenciais.email, credenciais.senha
    )
    
    if not nutricionista:
        logger.warning(f"Falha de login: {credenciais.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
        )
    
    # Criar tokens
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_service.create_access_token(
        data={"sub": nutricionista.email},
        expires_delta=access_token_expires
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": nutricionista.email}
    )
    
    logger.info(f"✅ Login bem-sucedido: {credenciais.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/cadastro", response_model=NutricionistaResponse, tags=["Autenticação"])
async def cadastro(
    dados: NutricionistaCadastro,
    db: Session = Depends(get_db)
):
    """
    Cadastro de novo nutricionista
    
    Args:
        dados: Dados de cadastro
        db: Sessão do banco
        
    Returns:
        NutricionistaResponse com dados do novo usuário
        
    Raises:
        HTTPException 400 se email já existe
    """
    # Registrar nutricionista
    nutricionista = auth_service.registrar_nutricionista(
        db,
        nome=dados.nome,
        crn=dados.crn,
        email=dados.email,
        telefone=dados.telefone,
        senha=dados.senha
    )
    
    if not nutricionista:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado ou erro ao registrar",
        )
    
    logger.info(f"✅ Novo nutricionista cadastrado: {dados.email}")
    
    return nutricionista

@router.post("/refresh", response_model=TokenResponse, tags=["Autenticação"])
async def refresh_token(
    dados: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Renovar access token usando refresh token
    
    Args:
        dados: Refresh token
        db: Sessão do banco
        
    Returns:
        Novo TokenResponse
        
    Raises:
        HTTPException 401 se refresh token inválido
    """
    payload = auth_service.decode_token(dados.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )
    
    email: str = payload.get("sub")
    
    # Criar novo access token
    access_token = auth_service.create_access_token(
        data={"sub": email},
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    
    return {
        "access_token": access_token,
        "refresh_token": dados.refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# ==================== ROTAS DE NUTRICIONISTA ====================

@router.get("/me", response_model=NutricionistaResponse, tags=["Nutricionista"])
async def obter_perfil(
    current_user: Nutricionista = Depends(get_current_user)
):
    """
    Obter perfil da nutricionista autenticada
    
    Args:
        current_user: Nutricionista autenticada
        
    Returns:
        NutricionistaResponse
    """
    return current_user

@router.get("/{nutricionista_id}", response_model=NutricionistaResponse, tags=["Nutricionista"])
async def obter_nutricionista(
    nutricionista_id: int,
    db: Session = Depends(get_db)
):
    """
    Obter informações de nutricionista por ID
    
    Args:
        nutricionista_id: ID da nutricionista
        db: Sessão do banco
        
    Returns:
        NutricionistaResponse
        
    Raises:
        HTTPException 404 se não encontrado
    """
    nutricionista = db.query(Nutricionista).filter(
        Nutricionista.id_nutricionista == nutricionista_id,
        Nutricionista.ativo == True
    ).first()
    
    if not nutricionista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutricionista não encontrado",
        )
    
    return nutricionista

@router.put("/me", response_model=NutricionistaResponse, tags=["Nutricionista"])
async def atualizar_perfil(
    dados: NutricionistaUpdate,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar perfil da nutricionista autenticada
    
    Args:
        dados: Dados para atualizar
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        NutricionistaResponse atualizado
    """
    try:
        # Atualizar apenas campos fornecidos
        if dados.nome:
            current_user.nome = dados.nome
        if dados.telefone:
            current_user.telefone = dados.telefone
        if dados.ativo is not None:
            current_user.ativo = dados.ativo
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ Perfil atualizado: {current_user.email}")
        
        return current_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar perfil",
        )

@router.delete("/", tags=["Nutricionista"])
async def desativar_conta(
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Desativar conta da nutricionista (soft delete)
    
    Args:
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        Mensagem de sucesso
    """
    try:
        current_user.ativo = False
        db.commit()
        
        logger.info(f"✅ Conta desativada: {current_user.email}")
        
        return {"message": "Conta desativada com sucesso"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao desativar conta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desativar conta",
        )

"""
Serviço de Autenticação com JWT
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging
from app.config import settings
from app.models import Nutricionista

logger = logging.getLogger(__name__)

# Configurar contexto de password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Serviço de autenticação e gerenciamento de tokens"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash uma senha usando bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar se uma senha corresponde ao hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Erro ao verificar password: {str(e)}")
            return False
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Criar token JWT de acesso
        
        Args:
            data: Dados para codificar no token
            expires_delta: Tempo de expiração customizado
            
        Returns:
            Token JWT
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Erro ao criar access token: {str(e)}")
            raise
    
    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any]
    ) -> str:
        """
        Criar token JWT de refresh
        
        Args:
            data: Dados para codificar no token
            
        Returns:
            Refresh token JWT
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Erro ao criar refresh token: {str(e)}")
            raise
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decodificar e validar um token JWT
        
        Args:
            token: Token JWT para decodificar
            
        Returns:
            Payload do token ou None se inválido
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"Erro ao decodificar token: {str(e)}")
            return None
    
    @staticmethod
    def autenticar_nutricionista(
        db: Session,
        email: str,
        senha: str
    ) -> Optional[Nutricionista]:
        """
        Autenticar nutricionista por email e senha
        
        Args:
            db: Sessão do banco
            email: Email do nutricionista
            senha: Senha em texto plano
            
        Returns:
            Objeto Nutricionista se válido, None caso contrário
        """
        try:
            nutricionista = db.query(Nutricionista).filter(
                Nutricionista.email == email,
                Nutricionista.ativo == True
            ).first()
            
            if not nutricionista:
                logger.warning(f"Tentativa de login com email não encontrado: {email}")
                return None
            
            if not AuthService.verify_password(senha, nutricionista.senha_hash):
                logger.warning(f"Tentativa de login com senha incorreta para: {email}")
                return None
            
            logger.info(f"✅ Nutricionista autenticado: {email}")
            return nutricionista
            
        except Exception as e:
            logger.error(f"Erro ao autenticar nutricionista: {str(e)}")
            return None
    
    @staticmethod
    def registrar_nutricionista(
        db: Session,
        nome: str,
        crn: str,
        email: str,
        telefone: str,
        senha: str
    ) -> Optional[Nutricionista]:
        """
        Registrar novo nutricionista
        
        Args:
            db: Sessão do banco
            nome: Nome completo
            crn: Número CRN
            email: Email (único)
            telefone: Telefone de contato
            senha: Senha em texto plano (será feito hash)
            
        Returns:
            Objeto Nutricionista criado ou None se erro
        """
        try:
            # Verificar se email já existe
            existente = db.query(Nutricionista).filter(
                Nutricionista.email == email
            ).first()
            
            if existente:
                logger.warning(f"Tentativa de cadastro com email já existente: {email}")
                return None
            
            # Criar novo nutricionista
            nutricionista = Nutricionista(
                nome=nome,
                crn=crn,
                email=email,
                telefone=telefone,
                senha_hash=AuthService.hash_password(senha),
                ativo=True,
                data_criacao=datetime.utcnow()
            )
            
            db.add(nutricionista)
            db.commit()
            db.refresh(nutricionista)
            
            logger.info(f"✅ Novo nutricionista cadastrado: {email}")
            return nutricionista
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao registrar nutricionista: {str(e)}")
            return None

# Instância global do serviço
auth_service = AuthService()

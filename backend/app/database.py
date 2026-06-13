"""
Configuração de banco de dados com SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Criar engine SQLAlchemy
if settings.ENVIRONMENT == "production":
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

# Criar SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()

# Função para testar conexão
def test_db_connection():
    """Testar conexão com banco de dados"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Conexão com banco de dados estabelecida com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {str(e)}")
        return False

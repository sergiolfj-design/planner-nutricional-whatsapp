"""
Configurações e variáveis de ambiente
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # ==================== AMBIENTE ====================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # ==================== API ====================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    API_PREFIX: str = "/api"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    # ==================== BANCO DE DADOS ====================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/planner_db"
    )
    
    # ==================== SEGURANÇA ====================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ==================== WHATSAPP ====================
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "verify_token_secret")
    WHATSAPP_API_URL: str = "https://graph.instagram.com/v18.0"
    
    # ==================== CORS ====================
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
    ]
    
    if ENVIRONMENT == "production":
        ALLOWED_ORIGINS = os.getenv(
            "ALLOWED_ORIGINS",
            "https://yourdomain.com"
        ).split(",")
    
    # ==================== EMAIL ====================
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@plannernuttricional.com")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    
    # ==================== AWS (opcional) ====================
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")
    
    # ==================== PDF ====================
    PDF_GENERATION_TIMEOUT: int = 30
    MAX_PDF_SIZE: int = 5 * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instância global de settings
settings = Settings()

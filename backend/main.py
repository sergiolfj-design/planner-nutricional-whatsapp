
"""
Sistema de Planner Nutricional via WhatsApp
Backend FastAPI - Main Application
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Importar routers
from app.routes import (
    nutricionista_routes,
    paciente_routes,
    meta_routes,
    planner_routes,
    dashboard_routes,
    whatsapp_routes,
)
from app.database import engine, SessionLocal, Base
from app.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar aplicação FastAPI
app = FastAPI(
    title="Planner Nutricional WhatsApp API",
    description="Sistema de acompanhamento nutricional integrado ao WhatsApp",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency para obter session do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== ROTAS ====================

# Incluir routers
app.include_router(
    nutricionista_routes.router,
    prefix="/api/nutricionistas",
    tags=["Nutricionistas"]
)

app.include_router(
    paciente_routes.router,
    prefix="/api/pacientes",
    tags=["Pacientes"]
)

app.include_router(
    meta_routes.router,
    prefix="/api/metas",
    tags=["Metas"]
)

app.include_router(
    planner_routes.router,
    prefix="/api/planners",
    tags=["Planners"]
)

app.include_router(
    dashboard_routes.router,
    prefix="/api/dashboards",
    tags=["Dashboards"]
)

app.include_router(
    whatsapp_routes.router,
    prefix="/api/whatsapp",
    tags=["WhatsApp"]
)

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Verificar status da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Planner Nutricional API"
    }

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Bem-vindo ao Planner Nutricional WhatsApp API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler customizado para HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler customizado para exceções gerais"""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "timestamp": datetime.now().isoformat()
        }
    )

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    logger.info("🚀 Iniciando Planner Nutricional API...")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Base de dados: {settings.DATABASE_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação"""
    logger.info("🛑 Encerrando Planner Nutricional API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )

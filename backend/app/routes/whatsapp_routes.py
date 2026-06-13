"""
Rotas de Integração com WhatsApp
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
import logging
import hmac
import hashlib
from app.database import SessionLocal
from app.services.whatsapp_service import whatsapp_service
from app.config import settings
from app.routes.nutricionista_routes import get_current_user
from app.models import Nutricionista

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== WEBHOOK VERIFICATION ====================

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(...),
    token: str = Query(...),
    challenge: str = Query(...)
):
    """
    Verificar webhook do WhatsApp
    
    Endpoint usado pelo WhatsApp para validar o webhook durante setup
    
    Args:
        mode: Modo (subscribe)
        token: Token de verificação
        challenge: Challenge para validar
        
    Returns:
        Challenge se válido
        
    Raises:
        HTTPException 403 se token inválido
    """
    if mode == "subscribe":
        if not whatsapp_service.validar_webhook_token(token):
            logger.warning(f"Tentativa de validação de webhook com token inválido")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token de verificação inválido",
            )
        
        logger.info("✅ Webhook WhatsApp verificado com sucesso")
        return int(challenge)
    
    logger.warning(f"Webhook chamado com modo não reconhecido: {mode}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Modo inválido",
    )

# ==================== WEBHOOK MESSAGES ====================

@router.post("/webhook")
async def webhook_whatsapp(request: Request):
    """
    Receber mensagens e eventos do WhatsApp
    
    Webhook para receber:
    - Mensagens enviadas por pacientes
    - Confirmações de entrega
    - Status de leitura
    
    Args:
        request: Requisição HTTP
        
    Returns:
        Confirmação de recebimento
    """
    try:
        # Obter payload
        body = await request.json()
        
        # Validar assinatura (opcional, mas recomendado)
        # signature = request.headers.get("X-Hub-Signature-256")
        # if not validar_assinatura(signature, body):
        #     raise HTTPException(status_code=403, detail="Assinatura inválida")
        
        # Log da mensagem recebida
        logger.info(f"📬 Mensagem recebida do WhatsApp: {body}")
        
        # TODO: Processar eventos:
        # - Mensagens de texto (paciente preenchendo planner)
        # - Confirmações de entrega
        # - Status de leitura
        # - Eventos de erro
        
        return {
            "success": True,
            "message": "Evento processado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook WhatsApp: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# ==================== ENVIAR MENSAGEM MANUALMENTE ====================

@router.post("/enviar-mensagem")
async def enviar_mensagem_manual(
    numero_destino: str,
    mensagem: str,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enviar mensagem de texto personalizada via WhatsApp
    
    Endpoint para nutricionista enviar mensagens personalizadas
    
    Args:
        numero_destino: Número WhatsApp do paciente
        mensagem: Conteúdo da mensagem
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        Status do envio
    """
    try:
        # Enviar via WhatsApp
        resultado = await whatsapp_service.enviar_mensagem_texto(
            numero_destino,
            mensagem
        )
        
        if resultado.get("success"):
            logger.info(f"✅ Mensagem enviada para {numero_destino}")
            return {
                "success": True,
                "message_id": resultado.get("message_id"),
                "timestamp": resultado.get("timestamp")
            }
        else:
            logger.error(f"Erro ao enviar mensagem: {resultado.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao enviar mensagem via WhatsApp",
            )
            
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar mensagem",
        )

# ==================== ENVIAR PLANNER ====================

@router.post("/enviar-planner/{planner_id}")
async def enviar_planner_via_whatsapp(
    planner_id: int,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enviar planner para paciente via WhatsApp
    
    Args:
        planner_id: ID do planner mensal
        current_user: Nutricionista autenticada
        db: Sessão do banco
        
    Returns:
        Status do envio
    """
    try:
        # TODO: Implementar
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Funcionalidade em desenvolvimento",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar planner: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar planner",
        )

# ==================== HEALTH CHECK ====================

@router.get("/health")
async def health_check():
    """Verificar se integração WhatsApp está funcionando"""
    return {
        "status": "healthy",
        "service": "WhatsApp Integration",
        "configured": bool(settings.WHATSAPP_ACCESS_TOKEN)
    }

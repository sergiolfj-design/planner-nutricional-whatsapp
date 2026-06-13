"""
Integração com WhatsApp Cloud API (Meta)
"""

import httpx
import logging
import json
from typing import Optional, Dict, Any
from app.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Serviço para integração com WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        
    @property
    def headers(self) -> Dict[str, str]:
        """Headers para requisições à API"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    async def enviar_mensagem_texto(
        self,
        numero_destino: str,
        texto: str,
        preview_url: bool = True
    ) -> Dict[str, Any]:
        """
        Enviar mensagem de texto ao paciente
        
        Args:
            numero_destino: Número WhatsApp do paciente (formato: +5521987654321)
            texto: Conteúdo da mensagem
            preview_url: Se deve fazer preview de URLs
            
        Returns:
            Resposta da API
        """
        try:
            # Normalizar número
            numero = numero_destino.strip()
            if not numero.startswith("+"):
                numero = f"+{numero}"
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": preview_url,
                    "body": texto
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    json=payload,
                    headers=self.headers
                )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Mensagem enviada para {numero}")
                return {
                    "success": True,
                    "message_id": response.json().get("messages", [{}])[0].get("id"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {response.text}")
                return {
                    "success": False,
                    "error": response.json(),
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Exceção ao enviar mensagem: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def enviar_modelo(
        self,
        numero_destino: str,
        nome_modelo: str,
        parametros: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Enviar mensagem usando template predefinido
        
        Args:
            numero_destino: Número WhatsApp do paciente
            nome_modelo: Nome do template na conta Meta
            parametros: Lista de parâmetros para o template
            
        Returns:
            Resposta da API
        """
        try:
            numero = numero_destino.strip()
            if not numero.startswith("+"):
                numero = f"+{numero}"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "template",
                "template": {
                    "name": nome_modelo,
                    "language": {
                        "code": "pt_BR"
                    }
                }
            }
            
            if parametros:
                payload["template"]["components"] = [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": str(p)} for p in parametros]
                    }
                ]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    json=payload,
                    headers=self.headers
                )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Template enviado para {numero}")
                return {
                    "success": True,
                    "message_id": response.json().get("messages", [{}])[0].get("id"),
                }
            else:
                logger.error(f"❌ Erro ao enviar template: {response.text}")
                return {
                    "success": False,
                    "error": response.json()
                }
                
        except Exception as e:
            logger.error(f"❌ Exceção ao enviar template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def enviar_planner_link(
        self,
        numero_destino: str,
        nome_paciente: str,
        link_planner: str,
        mes_ano: str
    ) -> Dict[str, Any]:
        """
        Enviar link do planner para o paciente
        
        Args:
            numero_destino: Número WhatsApp
            nome_paciente: Nome do paciente
            link_planner: URL do planner
            mes_ano: Mês e ano (formato: "Janeiro/2026")
            
        Returns:
            Resposta da API
        """
        mensagem = f"""
Olá {nome_paciente}! 👋

Seu planner nutricional de {mes_ano} está pronto!

📋 Clique aqui para preencher: {link_planner}

✨ Importante: Preencha um dia por vez no seu planner.

Qualquer dúvida, estou à disposição!

Abraços,
Sua Nutricionista
        """.strip()
        
        return await self.enviar_mensagem_texto(numero_destino, mensagem)
    
    async def enviar_lembrete(
        self,
        numero_destino: str,
        nome_paciente: str,
        link_planner: str
    ) -> Dict[str, Any]:
        """
        Enviar lembrete de preenchimento do planner
        
        Args:
            numero_destino: Número WhatsApp
            nome_paciente: Nome do paciente
            link_planner: URL do planner
            
        Returns:
            Resposta da API
        """
        mensagem = f"""
Oi {nome_paciente}! 🌟

Notei que seu planner ainda não foi preenchido hoje.

📱 Clique aqui para atualizar: {link_planner}

Vamos manter nossa consistência! 💪
        """.strip()
        
        return await self.enviar_mensagem_texto(numero_destino, mensagem)
    
    async def verificar_status_mensagem(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Verificar status de uma mensagem enviada
        
        Args:
            message_id: ID da mensagem retornado no envio
            
        Returns:
            Status da mensagem
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.api_url}/{message_id}",
                    headers=self.headers
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Erro ao verificar status: {response.text}")
                return {
                    "error": response.json()
                }
                
        except Exception as e:
            logger.error(f"❌ Exceção ao verificar status: {str(e)}")
            return {
                "error": str(e)
            }
    
    async def marcar_como_lido(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Marcar mensagem como lida
        
        Args:
            message_id: ID da mensagem recebida
            
        Returns:
            Resultado da operação
        """
        try:
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    json=payload,
                    headers=self.headers
                )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Mensagem marcada como lida: {message_id}")
                return {"success": True}
            else:
                return {"success": False, "error": response.json()}
                
        except Exception as e:
            logger.error(f"❌ Erro ao marcar como lido: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def validar_webhook_token(self, token: str) -> bool:
        """
        Validar token do webhook do WhatsApp
        
        Args:
            token: Token enviado pelo WhatsApp
            
        Returns:
            True se válido, False caso contrário
        """
        return token == settings.WHATSAPP_VERIFY_TOKEN

# Instância global do serviço
whatsapp_service = WhatsAppService()

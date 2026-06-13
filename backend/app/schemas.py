"""
Schemas Pydantic para validação de dados
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ==================== ENUMS ====================

class StatusPlanner(str, Enum):
    RASCUNHO = "rascunho"
    ENVIADO = "enviado"
    PREENCHIDO = "preenchido"
    FINALIZADO = "finalizado"

class StatusCumprimento(str, Enum):
    PENDENTE = "pendente"
    CUMPRIDA = "cumprida"
    NAO_CUMPRIDA = "não cumprida"
    OBSERVADA = "observada"

class StatusEnvio(str, Enum):
    PENDENTE = "pendente"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    FALHA = "falha"

# ==================== NUTRICIONISTA ====================

class NutricionistaCadastro(BaseModel):
    """Modelo para cadastro de nutricionista"""
    nome: str = Field(..., min_length=3, max_length=150)
    crn: str = Field(..., min_length=8, max_length=30)
    email: EmailStr
    telefone: str = Field(..., min_length=10, max_length=30)
    senha: str = Field(..., min_length=8, max_length=255)

class NutricionistaUpdate(BaseModel):
    """Modelo para atualização de nutricionista"""
    nome: Optional[str] = Field(None, min_length=3, max_length=150)
    telefone: Optional[str] = None
    ativo: Optional[bool] = None

class NutricionistaResponse(BaseModel):
    """Modelo de resposta para nutricionista"""
    id_nutricionista: int
    id_uuid: str
    nome: str
    crn: str
    email: str
    telefone: str
    ativo: bool
    data_criacao: datetime
    
    class Config:
        from_attributes = True

# ==================== PACIENTE ====================

class PacienteCadastro(BaseModel):
    """Modelo para cadastro de paciente"""
    nome: str = Field(..., min_length=3, max_length=150)
    whatsapp: str = Field(..., min_length=10, max_length=30)
    data_nascimento: Optional[datetime] = None
    objetivo_principal: Optional[str] = Field(None, max_length=255)
    observacoes: Optional[str] = None

class PacienteUpdate(BaseModel):
    """Modelo para atualização de paciente"""
    nome: Optional[str] = None
    whatsapp: Optional[str] = None
    objetivo_principal: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class PacienteResponse(BaseModel):
    """Modelo de resposta para paciente"""
    id_paciente: int
    id_uuid: str
    id_nutricionista: int
    nome: str
    whatsapp: str
    data_nascimento: Optional[datetime]
    objetivo_principal: Optional[str]
    observacoes: Optional[str]
    ativo: bool
    data_criacao: datetime
    
    class Config:
        from_attributes = True

# ==================== META ====================

class MetaCadastro(BaseModel):
    """Modelo para cadastro de meta"""
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    ativa: bool = True

class MetaResponse(BaseModel):
    """Modelo de resposta para meta"""
    id_meta: int
    id_nutricionista: int
    nome: str
    descricao: Optional[str]
    ativa: bool
    data_criacao: datetime
    
    class Config:
        from_attributes = True

# ==================== META PACIENTE ====================

class MetaPacienteAssociar(BaseModel):
    """Modelo para associar meta ao paciente"""
    id_meta: int
    ativa: bool = True

class MetaPacienteResponse(BaseModel):
    """Modelo de resposta para meta do paciente"""
    id_meta_paciente: int
    id_paciente: int
    id_meta: int
    ativa: bool
    meta_nome: str
    
    class Config:
        from_attributes = True

# ==================== REGISTRO DIÁRIO ====================

class RegistroDiarioCadastro(BaseModel):
    """Modelo para cadastro de registro diário"""
    dia: int = Field(..., ge=1, le=31)
    status_cumprimento: StatusCumprimento
    observacao: Optional[str] = None

class RegistroDiarioResponse(BaseModel):
    """Modelo de resposta para registro diário"""
    id_registro_diario: int
    id_planner_mensal: int
    id_meta_paciente: int
    dia: int
    status_cumprimento: str
    observacao: Optional[str]
    data_registro: datetime
    
    class Config:
        from_attributes = True

# ==================== PLANNER MENSAL ====================

class PlannerMensalCadastro(BaseModel):
    """Modelo para criação de planner mensal"""
    id_paciente: int
    mes: int = Field(..., ge=1, le=12)
    ano: int = Field(..., ge=2020)

class PlannerMensalResponse(BaseModel):
    """Modelo de resposta para planner mensal"""
    id_planner_mensal: int
    id_paciente: int
    id_nutricionista: int
    mes: int
    ano: int
    status: str
    paciente_nome: str
    nutricionista_nome: str
    data_criacao: datetime
    data_envio: Optional[datetime]
    
    class Config:
        from_attributes = True

class PlannerDetalhado(BaseModel):
    """Modelo detalhado de planner com registros"""
    planner: PlannerMensalResponse
    registros_diarios: List[RegistroDiarioResponse]
    metas_paciente: List[MetaPacienteResponse]

# ==================== DASHBOARD ====================

class DashboardResponse(BaseModel):
    """Modelo de resposta para dashboard"""
    id_dashboard: int
    id_planner_mensal: int
    percentual_aderencia: float
    total_metas_cumpridas: int
    total_metas_nao_cumpridas: int
    total_dias_preenchidos: int
    dias_criticos: Optional[str]
    sequencia_positiva: int
    evolucao_semanal: Optional[dict]
    data_geracao: datetime
    
    class Config:
        from_attributes = True

class DashboardDetalhado(BaseModel):
    """Dashboard detalhado com informações extras"""
    dashboard: DashboardResponse
    paciente_nome: str
    mes: int
    ano: int
    taxa_aprovacao: float

# ==================== MENSAGEM WHATSAPP ====================

class MensagemWhatsAppEnvio(BaseModel):
    """Modelo para envio de mensagem WhatsApp"""
    id_planner_mensal: int
    tipo_mensagem: str = "planner"

class MensagemWhatsAppResponse(BaseModel):
    """Modelo de resposta para mensagem WhatsApp"""
    id_mensagem_whatsapp: int
    id_paciente: int
    status_envio: str
    tipo_mensagem: str
    data_envio: datetime
    
    class Config:
        from_attributes = True

# ==================== LOGIN & AUTENTICAÇÃO ====================

class LoginRequest(BaseModel):
    """Modelo para requisição de login"""
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    """Modelo de resposta de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefreshRequest(BaseModel):
    """Modelo para refresh de token"""
    refresh_token: str

# ==================== RELATÓRIO PDF ====================

class RelatorioPDFResponse(BaseModel):
    """Modelo de resposta para relatório PDF"""
    id_relatorio: int
    id_planner_mensal: int
    nome_arquivo: str
    tamanho_bytes: int
    url_download: str
    data_geracao: datetime
    
    class Config:
        from_attributes = True

# ==================== WEBHOOK WHATSAPP ====================

class WebhookWhatsAppMessage(BaseModel):
    """Modelo para mensagem recebida do WhatsApp"""
    from_number: str
    message_type: str
    text: Optional[str] = None
    timestamp: int
    message_id: str
    phone_number_id: str

class WebhookWhatsAppResponse(BaseModel):
    """Modelo de resposta para webhook do WhatsApp"""
    success: bool
    message: str

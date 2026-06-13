"""
Modelos SQLAlchemy para o Planner Nutricional
Baseado na documentação de classes e BD
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, SmallInteger, Numeric, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base
import uuid

# ==================== NUTRICIONISTA ====================

class Nutricionista(Base):
    __tablename__ = "nutricionista"
    __table_args__ = (
        Index("idx_nutricionista_email", "email"),
    )
    
    id_nutricionista = Column(Integer, primary_key=True, index=True)
    id_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(150), nullable=False)
    crn = Column(String(30), unique=True, nullable=True)
    email = Column(String(150), unique=True, nullable=False)
    telefone = Column(String(30), nullable=True)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    pacientes = relationship("Paciente", back_populates="nutricionista")
    metas = relationship("Meta", back_populates="nutricionista")
    planners = relationship("PlannerMensal", back_populates="nutricionista")

# ==================== PACIENTE ====================

class Paciente(Base):
    __tablename__ = "paciente"
    __table_args__ = (
        Index("idx_paciente_nutricionista", "id_nutricionista"),
        Index("idx_paciente_whatsapp", "whatsapp"),
    )
    
    id_paciente = Column(Integer, primary_key=True, index=True)
    id_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    id_nutricionista = Column(Integer, ForeignKey("nutricionista.id_nutricionista"), nullable=False)
    nome = Column(String(150), nullable=False)
    whatsapp = Column(String(30), nullable=False)
    data_nascimento = Column(DateTime, nullable=True)
    objetivo_principal = Column(String(255), nullable=True)
    observacoes = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    nutricionista = relationship("Nutricionista", back_populates="pacientes")
    metas_paciente = relationship("MetaPaciente", back_populates="paciente")
    planners = relationship("PlannerMensal", back_populates="paciente")
    mensagens = relationship("MensagemWhatsApp", back_populates="paciente")

# ==================== META ====================

class Meta(Base):
    __tablename__ = "meta"
    __table_args__ = (
        Index("idx_meta_nutricionista", "id_nutricionista"),
    )
    
    id_meta = Column(Integer, primary_key=True, index=True)
    id_nutricionista = Column(Integer, ForeignKey("nutricionista.id_nutricionista"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    ativa = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    nutricionista = relationship("Nutricionista", back_populates="metas")
    metas_paciente = relationship("MetaPaciente", back_populates="meta")

# ==================== META PACIENTE ====================

class MetaPaciente(Base):
    __tablename__ = "meta_paciente"
    __table_args__ = (
        Index("idx_meta_paciente_paciente", "id_paciente"),
        Index("idx_meta_paciente_meta", "id_meta"),
    )
    
    id_meta_paciente = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_meta = Column(Integer, ForeignKey("meta.id_meta"), nullable=False)
    ativa = Column(Boolean, default=True)
    data_vinculo = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    paciente = relationship("Paciente", back_populates="metas_paciente")
    meta = relationship("Meta", back_populates="metas_paciente")
    registros = relationship("RegistroDiario", back_populates="meta_paciente")

# ==================== PLANNER MENSAL ====================

class PlannerMensal(Base):
    __tablename__ = "planner_mensal"
    __table_args__ = (
        Index("idx_planner_paciente_mes_ano", "id_paciente", "mes", "ano"),
    )
    
    id_planner_mensal = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_nutricionista = Column(Integer, ForeignKey("nutricionista.id_nutricionista"), nullable=False)
    mes = Column(SmallInteger, nullable=False)
    ano = Column(SmallInteger, nullable=False)
    status = Column(String(30), default="rascunho")  # rascunho, enviado, preenchido, finalizado
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_envio = Column(DateTime, nullable=True)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    paciente = relationship("Paciente", back_populates="planners")
    nutricionista = relationship("Nutricionista", back_populates="planners")
    registros_diarios = relationship("RegistroDiario", back_populates="planner")
    dashboard = relationship("Dashboard", back_populates="planner", uselist=False)
    mensagens = relationship("MensagemWhatsApp", back_populates="planner")
    relatorios = relationship("RelatorioPDF", back_populates="planner")

# ==================== REGISTRO DIÁRIO ====================

class RegistroDiario(Base):
    __tablename__ = "registro_diario"
    __table_args__ = (
        Index("idx_registro_planner_dia", "id_planner_mensal", "dia"),
    )
    
    id_registro_diario = Column(Integer, primary_key=True, index=True)
    id_planner_mensal = Column(Integer, ForeignKey("planner_mensal.id_planner_mensal"), nullable=False)
    id_meta_paciente = Column(Integer, ForeignKey("meta_paciente.id_meta_paciente"), nullable=False)
    dia = Column(SmallInteger, nullable=False)
    status_cumprimento = Column(String(30), default="pendente")  # cumprida, não cumprida, observada
    observacao = Column(Text, nullable=True)
    data_registro = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    planner = relationship("PlannerMensal", back_populates="registros_diarios")
    meta_paciente = relationship("MetaPaciente", back_populates="registros")

# ==================== DASHBOARD ====================

class Dashboard(Base):
    __tablename__ = "dashboard"
    
    id_dashboard = Column(Integer, primary_key=True, index=True)
    id_planner_mensal = Column(Integer, ForeignKey("planner_mensal.id_planner_mensal"), unique=True, nullable=False)
    percentual_aderencia = Column(Numeric(5, 2), default=0)
    total_metas_cumpridas = Column(Integer, default=0)
    total_metas_nao_cumpridas = Column(Integer, default=0)
    total_dias_preenchidos = Column(Integer, default=0)
    dias_criticos = Column(String(255), nullable=True)
    sequencia_positiva = Column(Integer, default=0)
    evolucao_semanal = Column(JSON, nullable=True)
    data_geracao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    planner = relationship("PlannerMensal", back_populates="dashboard")

# ==================== MENSAGEM WHATSAPP ====================

class MensagemWhatsApp(Base):
    __tablename__ = "mensagem_whatsapp"
    __table_args__ = (
        Index("idx_msg_status", "status_envio"),
    )
    
    id_mensagem_whatsapp = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_planner_mensal = Column(Integer, ForeignKey("planner_mensal.id_planner_mensal"), nullable=True)
    tipo_mensagem = Column(String(50), default="planner")  # planner, lembrete, confirmacao
    status_envio = Column(String(30), default="pendente")  # pendente, enviado, entregue, falha
    telefone_destino = Column(String(30), nullable=False)
    payload_enviado = Column(JSON, nullable=True)
    resposta_api = Column(JSON, nullable=True)
    data_envio = Column(DateTime, default=datetime.utcnow)
    data_entrega = Column(DateTime, nullable=True)
    
    # Relacionamentos
    paciente = relationship("Paciente", back_populates="mensagens")
    planner = relationship("PlannerMensal", back_populates="mensagens")

# ==================== RELATÓRIO PDF ====================

class RelatorioPDF(Base):
    __tablename__ = "relatorio_pdf"
    
    id_relatorio = Column(Integer, primary_key=True, index=True)
    id_planner_mensal = Column(Integer, ForeignKey("planner_mensal.id_planner_mensal"), nullable=False)
    caminho_arquivo = Column(String(255), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    tamanho_bytes = Column(Integer, default=0)
    data_geracao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    planner = relationship("PlannerMensal", back_populates="relatorios")

# ==================== LOG DE EVENTOS ====================

class LogEvento(Base):
    __tablename__ = "log_evento"
    
    id_log_evento = Column(Integer, primary_key=True, index=True)
    entidade = Column(String(100), nullable=False)
    tipo_evento = Column(String(100), nullable=False)
    id_entidade = Column(Integer, nullable=True)
    usuario_id = Column(Integer, nullable=True)
    payload = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    data_evento = Column(DateTime, default=datetime.utcnow)

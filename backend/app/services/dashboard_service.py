"""
Serviço para geração de dashboards com métricas nutricionais
"""

import logging
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import (
    PlannerMensal, RegistroDiario, Dashboard, MetaPaciente
)

logger = logging.getLogger(__name__)

class DashboardService:
    """Serviço para cálculo de métricas e geração de dashboards"""
    
    @staticmethod
    def calcular_percentual_aderencia(
        registros: List[RegistroDiario]
    ) -> float:
        """
        Calcular percentual de aderência baseado nos registros
        
        Args:
            registros: Lista de registros diários
            
        Returns:
            Percentual de aderência (0-100)
        """
        if not registros:
            return 0.0
        
        cumpridas = len([r for r in registros if r.status_cumprimento == "cumprida"])
        total = len(registros)
        
        percentual = (cumpridas / total) * 100 if total > 0 else 0
        return round(percentual, 2)
    
    @staticmethod
    def contar_metas(
        registros: List[RegistroDiario]
    ) -> tuple[int, int]:
        """
        Contar metas cumpridas e não cumpridas
        
        Args:
            registros: Lista de registros diários
            
        Returns:
            Tupla (cumpridas, não cumpridas)
        """
        cumpridas = len([r for r in registros if r.status_cumprimento == "cumprida"])
        nao_cumpridas = len([r for r in registros if r.status_cumprimento == "não cumprida"])
        
        return cumpridas, nao_cumpridas
    
    @staticmethod
    def identificar_dias_criticos(
        registros: List[RegistroDiario],
        limiar: float = 0.5
    ) -> List[int]:
        """
        Identificar dias onde aderência foi baixa
        
        Args:
            registros: Lista de registros
            limiar: Percentual mínimo para não ser crítico (padrão 50%)
            
        Returns:
            Lista de dias críticos
        """
        # Agrupar registros por dia
        dias = {}
        for registro in registros:
            if registro.dia not in dias:
                dias[registro.dia] = []
            dias[registro.dia].append(registro)
        
        dias_criticos = []
        for dia, regs in dias.items():
            cumpridas = len([r for r in regs if r.status_cumprimento == "cumprida"])
            taxa = cumpridas / len(regs) if regs else 0
            
            if taxa < limiar:
                dias_criticos.append(dia)
        
        return sorted(dias_criticos)
    
    @staticmethod
    def calcular_sequencia_positiva(
        registros: List[RegistroDiario]
    ) -> int:
        """
        Calcular maior sequência de dias com todas as metas cumpridas
        
        Args:
            registros: Lista de registros
            
        Returns:
            Quantidade de dias em sequência
        """
        if not registros:
            return 0
        
        # Agrupar por dia
        dias_ordenados = sorted(set(r.dia for r in registros))
        
        max_sequencia = 0
        sequencia_atual = 0
        
        for dia in dias_ordenados:
            regs_dia = [r for r in registros if r.dia == dia]
            cumpridas = len([r for r in regs_dia if r.status_cumprimento == "cumprida"])
            
            if cumpridas == len(regs_dia):
                sequencia_atual += 1
                max_sequencia = max(max_sequencia, sequencia_atual)
            else:
                sequencia_atual = 0
        
        return max_sequencia
    
    @staticmethod
    def calcular_evolucao_semanal(
        registros: List[RegistroDiario]
    ) -> Dict[int, float]:
        """
        Calcular aderência por semana do mês
        
        Args:
            registros: Lista de registros
            
        Returns:
            Dicionário com semana como chave e percentual como valor
        """
        if not registros:
            return {}
        
        evolucao = {}
        
        # Agrupar por semana (1-5)
        for registro in registros:
            semana = (registro.dia - 1) // 7 + 1
            
            if semana not in evolucao:
                evolucao[semana] = {"cumpridas": 0, "total": 0}
            
            evolucao[semana]["total"] += 1
            if registro.status_cumprimento == "cumprida":
                evolucao[semana]["cumpridas"] += 1
        
        # Calcular percentual por semana
        resultado = {}
        for semana, dados in evolucao.items():
            percentual = (dados["cumpridas"] / dados["total"] * 100) if dados["total"] > 0 else 0
            resultado[semana] = round(percentual, 2)
        
        return resultado
    
    @staticmethod
    def gerar_dashboard(
        db: Session,
        planner_id: int
    ) -> Dict[str, Any]:
        """
        Gerar dashboard completo para um planner
        
        Args:
            db: Sessão do banco
            planner_id: ID do planner mensal
            
        Returns:
            Dicionário com todas as métricas
        """
        try:
            # Buscar planner
            planner = db.query(PlannerMensal).filter(
                PlannerMensal.id_planner_mensal == planner_id
            ).first()
            
            if not planner:
                logger.error(f"Planner {planner_id} não encontrado")
                return None
            
            # Buscar registros diários
            registros = db.query(RegistroDiario).filter(
                RegistroDiario.id_planner_mensal == planner_id
            ).all()
            
            # Calcular todas as métricas
            percentual = DashboardService.calcular_percentual_aderencia(registros)
            cumpridas, nao_cumpridas = DashboardService.contar_metas(registros)
            dias_criticos = DashboardService.identificar_dias_criticos(registros)
            sequencia = DashboardService.calcular_sequencia_positiva(registros)
            evolucao = DashboardService.calcular_evolucao_semanal(registros)
            
            # Verificar ou criar dashboard no BD
            dashboard = db.query(Dashboard).filter(
                Dashboard.id_planner_mensal == planner_id
            ).first()
            
            if dashboard:
                # Atualizar
                dashboard.percentual_aderencia = percentual
                dashboard.total_metas_cumpridas = cumpridas
                dashboard.total_metas_nao_cumpridas = nao_cumpridas
                dashboard.total_dias_preenchidos = len(set(r.dia for r in registros))
                dashboard.dias_criticos = ",".join(map(str, dias_criticos)) if dias_criticos else None
                dashboard.sequencia_positiva = sequencia
                dashboard.evolucao_semanal = evolucao
                dashboard.data_atualizacao = datetime.utcnow()
            else:
                # Criar novo
                dashboard = Dashboard(
                    id_planner_mensal=planner_id,
                    percentual_aderencia=percentual,
                    total_metas_cumpridas=cumpridas,
                    total_metas_nao_cumpridas=nao_cumpridas,
                    total_dias_preenchidos=len(set(r.dia for r in registros)),
                    dias_criticos=",".join(map(str, dias_criticos)) if dias_criticos else None,
                    sequencia_positiva=sequencia,
                    evolucao_semanal=evolucao,
                    data_geracao=datetime.utcnow()
                )
            
            db.add(dashboard)
            db.commit()
            db.refresh(dashboard)
            
            logger.info(f"✅ Dashboard gerado para planner {planner_id}")
            
            return {
                "id_dashboard": dashboard.id_dashboard,
                "percentual_aderencia": float(dashboard.percentual_aderencia),
                "total_metas_cumpridas": dashboard.total_metas_cumpridas,
                "total_metas_nao_cumpridas": dashboard.total_metas_nao_cumpridas,
                "total_dias_preenchidos": dashboard.total_dias_preenchidos,
                "dias_criticos": dias_criticos,
                "sequencia_positiva": dashboard.sequencia_positiva,
                "evolucao_semanal": evolucao,
                "data_geracao": dashboard.data_geracao.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard: {str(e)}")
            return None
    
    @staticmethod
    def obter_diagnostico(percentual_aderencia: float) -> Dict[str, str]:
        """
        Obter diagnóstico baseado no percentual
        
        Args:
            percentual_aderencia: Percentual (0-100)
            
        Returns:
            Dicionário com diagnóstico e recomendação
        """
        if percentual_aderencia >= 80:
            return {
                "status": "Excelente",
                "cor": "green",
                "recomendacao": "Parabéns! Você está com ótima aderência. Mantenha o ritmo! 🎉"
            }
        elif percentual_aderencia >= 60:
            return {
                "status": "Bom",
                "cor": "blue",
                "recomendacao": "Você está indo bem! Vamos melhorar ainda mais? 💪"
            }
        elif percentual_aderencia >= 40:
            return {
                "status": "Regular",
                "cor": "orange",
                "recomendacao": "Vamos reforçar o compromisso? Você consegue! 🌟"
            }
        else:
            return {
                "status": "Baixo",
                "cor": "red",
                "recomendacao": "Precisa de ajuda? Vamos conversar sobre desafios. 🤝"
            }

# Instância global do serviço
dashboard_service = DashboardService()

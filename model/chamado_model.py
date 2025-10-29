from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class StatusChamado(Enum):
    ABERTO = "Aberto"
    EM_ANALISE = "Em Análise"
    RESOLVIDO = "Resolvido"
    FECHADO = "Fechado"

class PrioridadeChamado(Enum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    URGENTE = "Urgente"


@dataclass
class Chamado:
    id: int
    titulo: str
    status: StatusChamado
    prioridade: PrioridadeChamado
    usuario_id: int
    data_abertura: Optional[datetime] = None
    data_fechamento: Optional[datetime] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None
    mensagens_nao_lidas: int = 0
    tem_resposta_admin: bool = False

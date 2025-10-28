from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from model.chamado_model import StatusChamado


class TipoInteracao(Enum):
    ABERTURA = "Abertura"
    RESPOSTA_USUARIO = "Resposta do Usuário"
    RESPOSTA_ADMIN = "Resposta do Administrador"


@dataclass
class ChamadoInteracao:
    id: int
    chamado_id: int
    usuario_id: int
    mensagem: str
    tipo: TipoInteracao
    data_interacao: datetime
    status_resultante: Optional[StatusChamado] = None
    data_leitura: Optional[datetime] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None

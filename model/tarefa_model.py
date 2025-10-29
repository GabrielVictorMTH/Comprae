from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Tarefa:
    id: int
    titulo: str
    descricao: str
    concluida: bool
    usuario_id: int
    data_criacao: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None

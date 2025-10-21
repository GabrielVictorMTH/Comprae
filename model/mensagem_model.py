from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.usuario_model import Usuario


@dataclass
class Mensagem:
    id_mensagem: int
    id_remetente: int
    id_destinatario: int
    mensagem: str
    data_hora: datetime
    visualizada: bool
    # Relacionamentos
    remetente: Optional[Usuario]
    destinatario: Optional[Usuario]
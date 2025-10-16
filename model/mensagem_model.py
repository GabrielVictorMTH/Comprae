from dataclasses import dataclass
from datetime import datetime


@dataclass
class Mensagem:
    id_mensagem: int
    id_remetente: int
    id_destinatario: int
    mensagem: str
    data_hora: datetime
    visualizada: bool
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Curtida:
    id: int
    id_usuario: int
    id_anuncio: int
    data_curtida: datetime
    
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Curtida:
    id_usuario: int
    id_anuncio: int
    data_curtida: Optional[datetime] = None
    
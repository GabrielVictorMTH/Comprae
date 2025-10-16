from dataclasses import dataclass
from datetime import datetime


@dataclass

class Anuncio:
    id_anuncio: int
    id_vendedor: int
    id_categoria: int
    nome: str
    discricao: str
    peso: str
    preco: float
    estoque: str
    data_cadastro: datetime
    ativo: bool

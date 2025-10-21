from argparse import OPTIONAL
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.categoria_model import Categoria
from model.usuario_model import Usuario


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
    # Relacionamento
    vendedor: Optional[Usuario]
    categoria: Optional[Categoria]
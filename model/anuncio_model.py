from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.categoria_model import Categoria
from model.usuario_model import Usuario


@dataclass
class Anuncio:
    id: int
    id_vendedor: int
    id_categoria: int
    nome: str
    descricao: str
    peso: float
    preco: float
    estoque: int
    data_cadastro: datetime
    ativo: bool
    # Relacionamentos
    vendedor: Optional[Usuario] = None
    categoria: Optional[Categoria] = None
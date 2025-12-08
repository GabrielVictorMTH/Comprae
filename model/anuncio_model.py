from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from model.usuario_model import Usuario

if TYPE_CHECKING:
    from model.categoria_model import Categoria


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
    categoria: Optional["Categoria"] = None
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.anuncio_model import Anuncio
from model.endereco_model import Endereco
from model.usuario_model import Usuario


@dataclass
class Pedido:
    id_pedido: int
    id_endereco: int
    id_comprador: int
    id_anuncio: int
    preco: float
    status: str
    # Campos opcionais
    data_hora_pedido: Optional[datetime] = None
    data_hora_pagamento: Optional[datetime] = None
    data_hora_envio: Optional[datetime] = None
    codigo_rastreio: Optional[str] = None
    nota_avaliacao: Optional[int] = None
    comentario_avaliacao: Optional[str] = None
    data_hora_avaliacao: Optional[datetime] = None
    # Relacionamentos
    endereco: Optional[Endereco] = None
    comprador: Optional[Usuario] = None
    anuncio: Optional[Anuncio] = None
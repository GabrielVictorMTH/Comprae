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
    data_hora_pedido: datetime
    data_hora_pagamento: datetime
    data_hora_envio: datetime
    codigo_rastreio: str
    nota_avaliacao: int
    comentario_avaliacao: str
    data_hora_avaliacao: datetime

    endereco: Optional[Endereco]
    comprador: Optional[Usuario]
    anuncio: Optional[Anuncio]
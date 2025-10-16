from dataclasses import dataclass
from datetime import datetime


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
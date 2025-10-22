"""
Repositório para operações com pedidos.
"""
from typing import Optional
from datetime import datetime

from model.pedido_model import Pedido
from sql.pedido_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de pedidos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(pedido: Pedido) -> Optional[int]:
    """Insere um novo pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (
                pedido.id_endereco,
                pedido.id_comprador,
                pedido.id_anuncio,
                pedido.preco
            )
        )
        return cursor.lastrowid


def atualizar_status(id_pedido: int, status: str) -> bool:
    """Atualiza o status de um pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (status, id_pedido))
        return cursor.rowcount > 0


def marcar_como_pago(id_pedido: int) -> bool:
    """Marca pedido como pago e registra data/hora"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_PARA_PAGO, (id_pedido,))
        return cursor.rowcount > 0


def marcar_como_enviado(id_pedido: int, codigo_rastreio: str) -> bool:
    """Marca pedido como enviado com código de rastreio"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_PARA_ENVIADO, (codigo_rastreio, id_pedido))
        return cursor.rowcount > 0


def cancelar(id_pedido: int) -> bool:
    """Cancela um pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CANCELAR_PEDIDO, (id_pedido,))
        return cursor.rowcount > 0


def avaliar(id_pedido: int, nota: int, comentario: str) -> bool:
    """Registra avaliação de um pedido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(AVALIAR_PEDIDO, (nota, comentario, id_pedido))
        return cursor.rowcount > 0


def obter_por_id(id_pedido: int) -> Optional[Pedido]:
    """Obtém um pedido por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_pedido,))
        row = cursor.fetchone()
        if row:
            return _row_to_pedido(row)
        return None


def obter_por_comprador(id_comprador: int) -> list[Pedido]:
    """Obtém todos os pedidos de um comprador"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_COMPRADOR, (id_comprador,))
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def obter_por_vendedor(id_vendedor: int) -> list[Pedido]:
    """Obtém todos os pedidos relacionados aos anúncios de um vendedor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_VENDEDOR, (id_vendedor,))
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def obter_por_status(status: str) -> list[Pedido]:
    """Obtém pedidos por status"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_STATUS, (status,))
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def obter_todos() -> list[Pedido]:
    """Obtém todos os pedidos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_pedido(row) for row in rows]


def _converter_data(data_str: Optional[str]) -> Optional[datetime]:
    """Converte string de data do banco em objeto datetime"""
    if not data_str:
        return None
    try:
        return datetime.fromisoformat(data_str)
    except (ValueError, AttributeError):
        return None


def _row_to_pedido(row) -> Pedido:
    """Converte row do banco para objeto Pedido"""
    return Pedido(
        id_pedido=row["id_pedido"],
        id_endereco=row["id_endereco"],
        id_comprador=row["id_comprador"],
        id_anuncio=row["id_anuncio"],
        preco=row["preco"],
        status=row["status"],
        data_hora_pedido=_converter_data(row["data_hora_pedido"]),
        data_hora_pagamento=_converter_data(row["data_hora_pagamento"] if "data_hora_pagamento" in row.keys() else None),
        data_hora_envio=_converter_data(row["data_hora_envio"] if "data_hora_envio" in row.keys() else None),
        codigo_rastreio=row["codigo_rastreio"] if "codigo_rastreio" in row.keys() else None,
        nota_avaliacao=row["nota_avaliacao"] if "nota_avaliacao" in row.keys() else None,
        comentario_avaliacao=row["comentario_avaliacao"] if "comentario_avaliacao" in row.keys() else None,
        data_hora_avaliacao=_converter_data(row["data_hora_avaliacao"] if "data_hora_avaliacao" in row.keys() else None),
        endereco=None,
        comprador=None,
        anuncio=None
    )

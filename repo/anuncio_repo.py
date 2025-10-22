"""
Repositório para operações com anúncios (produtos).
"""
from typing import Optional
from datetime import datetime

from model.anuncio_model import Anuncio
from sql.anuncio_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de anúncios e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICE_VENDEDOR)
        cursor.execute(CRIAR_INDICE_CATEGORIA)
        cursor.execute(CRIAR_INDICE_ATIVO)
        return True


def inserir(anuncio: Anuncio) -> Optional[Anuncio]:
    """Insere um novo anúncio"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (
                anuncio.id_vendedor,
                anuncio.id_categoria,
                anuncio.nome,
                anuncio.discricao,  # Note: usar campo do model atual (com typo)
                anuncio.peso,
                anuncio.preco,
                anuncio.estoque
            )
        )
        if cursor.lastrowid:
            return obter_por_id(cursor.lastrowid)
        return None


def alterar(anuncio: Anuncio) -> bool:
    """Altera um anúncio existente"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ALTERAR,
            (
                anuncio.id_categoria,
                anuncio.nome,
                anuncio.discricao,
                anuncio.peso,
                anuncio.preco,
                anuncio.estoque,
                anuncio.ativo,
                anuncio.id_anuncio
            )
        )
        return cursor.rowcount > 0


def excluir(id_anuncio: int) -> bool:
    """Exclui um anúncio"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_anuncio,))
        return cursor.rowcount > 0


def obter_por_id(id_anuncio: int) -> Optional[Anuncio]:
    """Obtém um anúncio por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_anuncio,))
        row = cursor.fetchone()
        if row:
            return _row_to_anuncio(row)
        return None


def obter_todos() -> list[Anuncio]:
    """Obtém todos os anúncios"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_todos_ativos() -> list[Anuncio]:
    """Obtém apenas anúncios ativos com estoque"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_ATIVOS)
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_por_vendedor(id_vendedor: int) -> list[Anuncio]:
    """Obtém todos os anúncios de um vendedor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_VENDEDOR, (id_vendedor,))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_por_categoria(id_categoria: int) -> list[Anuncio]:
    """Obtém anúncios ativos de uma categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CATEGORIA, (id_categoria,))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def buscar_por_nome(termo: str) -> list[Anuncio]:
    """Busca anúncios por nome (LIKE)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(BUSCAR_POR_NOME, (f"%{termo}%",))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def buscar_com_filtros(
    termo: Optional[str] = None,
    id_categoria: Optional[int] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None
) -> list[Anuncio]:
    """Busca anúncios com filtros opcionais"""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Preparar parâmetros para query SQL com IS NULL checks
        termo_like = f"%{termo}%" if termo else None
        cursor.execute(
            BUSCAR_COM_FILTROS,
            (
                termo_like, termo_like,
                id_categoria, id_categoria,
                preco_min, preco_min,
                preco_max, preco_max
            )
        )
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def atualizar_estoque(id_anuncio: int, quantidade: int) -> bool:
    """
    Diminui o estoque de um anúncio de forma atômica.
    Retorna True se conseguiu atualizar (estoque suficiente).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_ESTOQUE, (quantidade, id_anuncio, quantidade))
        return cursor.rowcount > 0


def _row_to_anuncio(row) -> Anuncio:
    """Converte row do banco para objeto Anuncio"""
    return Anuncio(
        id_anuncio=row["id_anuncio"],
        id_vendedor=row["id_vendedor"],
        id_categoria=row["id_categoria"],
        nome=row["nome"],
        discricao=row["descricao"],  # Note: SQL usa "descricao" corrigido
        peso=row["peso"],
        preco=row["preco"],
        estoque=row["estoque"],
        data_cadastro=datetime.fromisoformat(row["data_cadastro"]),
        ativo=bool(row["ativo"]),
        vendedor=None,
        categoria=None
    )
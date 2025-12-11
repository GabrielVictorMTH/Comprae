"""
Repositório para operações com anúncios (produtos).
"""
from typing import Optional
from datetime import datetime

from model.anuncio_model import Anuncio
from sql import anuncio_sql
from sql.anuncio_sql import *
from util.db_util import obter_conexao


def criar_tabela() -> bool:
    """Cria a tabela de anúncios"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(anuncio: Anuncio) -> Optional[Anuncio]:
    """Insere um novo anúncio"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (
                anuncio.id_vendedor,
                anuncio.id_categoria,
                anuncio.nome,
                anuncio.descricao,
                anuncio.peso,
                anuncio.preco,
                anuncio.estoque
            )
        )
        anuncio_id = cursor.lastrowid

    # Buscar o anúncio inserido após commit
    if anuncio_id:
        return obter_por_id(anuncio_id)
    return None


def alterar(anuncio: Anuncio) -> bool:
    """Altera um anúncio existente"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ALTERAR,
            (
                anuncio.id_categoria,
                anuncio.nome,
                anuncio.descricao,
                anuncio.peso,
                anuncio.preco,
                anuncio.estoque,
                anuncio.ativo,
                anuncio.id
            )
        )
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """Exclui um anúncio"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def obter_por_id(id: int) -> Optional[Anuncio]:
    """Obtém um anúncio por ID"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_anuncio(row)
        return None


def obter_todos() -> list[Anuncio]:
    """Obtém todos os anúncios"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_todos_ativos() -> list[Anuncio]:
    """Obtém apenas anúncios ativos com estoque"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_ATIVOS)
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_por_vendedor(id_vendedor: int) -> list[Anuncio]:
    """Obtém todos os anúncios de um vendedor"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_VENDEDOR, (id_vendedor,))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_por_categoria(id_categoria: int) -> list[Anuncio]:
    """Obtém anúncios ativos de uma categoria"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CATEGORIA, (id_categoria,))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def buscar_por_nome(termo: str) -> list[Anuncio]:
    """Busca anúncios por nome (LIKE)"""
    with obter_conexao() as conn:
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
    with obter_conexao() as conn:
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


def atualizar_estoque(id: int, quantidade: int) -> bool:
    """
    Diminui o estoque de um anúncio de forma atômica.
    Retorna True se conseguiu atualizar (estoque suficiente).
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_ESTOQUE, (quantidade, id, quantidade))
        return cursor.rowcount > 0


def obter_ativos_paginados(
    pagina: int = 1,
    por_pagina: int = 12,
    termo: Optional[str] = None,
    id_categoria: Optional[int] = None
) -> tuple[list[Anuncio], int]:
    """
    Obtém anúncios ativos com paginação e filtros.

    Returns:
        Tupla com (lista de anúncios, total de registros)
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()

        # Preparar parâmetros de busca
        termo_like = f"%{termo}%" if termo else None
        offset = (pagina - 1) * por_pagina

        # Buscar anúncios paginados
        cursor.execute(
            OBTER_ATIVOS_PAGINADOS,
            (
                termo_like, termo_like, termo_like,  # termo para nome e descricao
                id_categoria, id_categoria,           # categoria
                por_pagina, offset                    # paginacao
            )
        )
        rows = cursor.fetchall()
        anuncios = [_row_to_anuncio(row) for row in rows]

        # Contar total
        cursor.execute(
            CONTAR_ATIVOS,
            (
                termo_like, termo_like, termo_like,
                id_categoria, id_categoria
            )
        )
        total = cursor.fetchone()["total"]

        return anuncios, total


def obter_ultimos_ativos(limite: int = 12) -> list[Anuncio]:
    """Obtém os últimos anúncios ativos (para home page)"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ULTIMOS_ATIVOS, (limite,))
        rows = cursor.fetchall()
        return [_row_to_anuncio(row) for row in rows]


def obter_por_id_com_detalhes(id: int) -> Optional[Anuncio]:
    """Obtém anúncio por ID com dados do vendedor e categoria"""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID_COM_DETALHES, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_anuncio(row)
        return None


def _row_to_anuncio(row) -> Anuncio:
    """Converte row do banco para objeto Anuncio"""
    anuncio = Anuncio(
        id=row["id"],
        id_vendedor=row["id_vendedor"],
        id_categoria=row["id_categoria"],
        nome=row["nome"],
        descricao=row["descricao"],
        peso=row["peso"],
        preco=row["preco"],
        estoque=row["estoque"],
        data_cadastro=datetime.fromisoformat(row["data_cadastro"]),
        ativo=bool(row["ativo"]),
        vendedor=None,
        categoria=None
    )
    # Adicionar campos extras se presentes no resultado
    keys = row.keys()
    if "nome_categoria" in keys:
        anuncio.nome_categoria = row["nome_categoria"]
    if "nome_vendedor" in keys:
        anuncio.nome_vendedor = row["nome_vendedor"]
    if "email_vendedor" in keys:
        anuncio.email_vendedor = row["email_vendedor"]
    return anuncio
    
    from sql import anuncio_sql
    
    def incrementar_visualizacoes(id: int) -> bool:
       """Incrementa o contador de visualizacoes de um anuncio"""
       with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(anuncio_sql.INCREMENTAR_VISUALIZACOES, (id,))
        return cursor.rowcount > 0
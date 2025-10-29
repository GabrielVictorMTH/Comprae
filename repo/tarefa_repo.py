from datetime import datetime
from typing import Optional
from model.tarefa_model import Tarefa
from sql.tarefa_sql import *
from util.db_util import get_connection


def _row_to_tarefa(row) -> Tarefa:
    """
    Converte uma linha do banco de dados em objeto Tarefa.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto Tarefa populado
    """
    # Campos do JOIN (opcionais)
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None
    usuario_email = row["usuario_email"] if "usuario_email" in row.keys() else None

    return Tarefa(
        id=row["id"],
        titulo=row["titulo"],
        descricao=row["descricao"],
        concluida=bool(row["concluida"]),
        usuario_id=row["usuario_id"],
        data_criacao=row["data_criacao"],
        data_conclusao=row["data_conclusao"],
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )


def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(tarefa: Tarefa) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            tarefa.titulo,
            tarefa.descricao,
            tarefa.usuario_id
        ))
        return cursor.lastrowid

def obter_todos_por_usuario(usuario_id: int) -> list[Tarefa]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_POR_USUARIO, (usuario_id,))
        rows = cursor.fetchall()
        return [_row_to_tarefa(row) for row in rows]

def obter_por_id(id: int) -> Optional[Tarefa]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_tarefa(row)
        return None

def atualizar(tarefa: Tarefa) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            tarefa.titulo,
            tarefa.descricao,
            tarefa.concluida,
            tarefa.id
        ))
        return cursor.rowcount > 0

def marcar_concluida(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_CONCLUIDA, (id,))
        return cursor.rowcount > 0

def excluir(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0

def contar_pendentes_por_usuario(usuario_id: int) -> int:
    """
    Conta quantas tarefas não concluídas um usuário possui.

    Args:
        usuario_id: ID do usuário

    Returns:
        Número de tarefas com concluida = 0
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as total FROM tarefa WHERE usuario_id = ? AND concluida = 0",
            (usuario_id,)
        )
        row = cursor.fetchone()
        return row["total"] if row else 0

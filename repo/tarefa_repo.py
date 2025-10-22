from datetime import datetime
from typing import Optional
from model.tarefa_model import Tarefa
from sql.tarefa_sql import *
from util.db_util import get_connection

def _converter_data(data_str: Optional[str]) -> Optional[datetime]:
    """Converte string de data do banco em objeto datetime"""
    if not data_str:
        return None
    try:
        # SQLite retorna datas no formato 'YYYY-MM-DD HH:MM:SS'
        return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

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
        return [
            Tarefa(
                id=row["id"],
                titulo=row["titulo"],
                descricao=row["descricao"],
                concluida=bool(row["concluida"]),
                usuario_id=row["usuario_id"],
                data_criacao=_converter_data(row["data_criacao"]),
                data_conclusao=_converter_data(row["data_conclusao"])
            )
            for row in rows
        ]

def obter_por_id(id: int) -> Optional[Tarefa]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return Tarefa(
                id=row["id"],
                titulo=row["titulo"],
                descricao=row["descricao"],
                concluida=bool(row["concluida"]),
                usuario_id=row["usuario_id"],
                data_criacao=_converter_data(row["data_criacao"]),
                data_conclusao=_converter_data(row["data_conclusao"])
            )
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

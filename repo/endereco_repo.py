"""
Repository para operações com Endereços.
"""
from typing import Optional
from model.endereco_model import Endereco
from sql.endereco_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de endereços"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(endereco: Endereco) -> Optional[int]:
    """Insere um novo endereço"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            endereco.id_usuario,
            endereco.titulo,
            endereco.logradouro,
            endereco.numero,
            endereco.complemento,
            endereco.bairro,
            endereco.cidade,
            endereco.uf,
            endereco.cep
        ))
        return cursor.lastrowid


def alterar(endereco: Endereco) -> bool:
    """Altera um endereço existente"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (
            endereco.titulo,
            endereco.logradouro,
            endereco.numero,
            endereco.complemento,
            endereco.bairro,
            endereco.cidade,
            endereco.uf,
            endereco.cep,
            endereco.id_endereco
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """Exclui um endereço"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def obter_por_id(id: int) -> Optional[Endereco]:
    """Obtém endereço por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return Endereco(
                id_endereco=row["id_endereco"],
                id_usuario=row["id_usuario"],
                titulo=row["titulo"],
                logradouro=row["logradouro"],
                numero=row["numero"],
                complemento=row["complemento"],
                bairro=row["bairro"],
                cidade=row["cidade"],
                uf=row["uf"],
                cep=row["cep"],
                usuario=None  # Não carrega relacionamento aqui
            )
        return None


def obter_por_usuario(id_usuario: int) -> list[Endereco]:
    """Obtém todos os endereços de um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_POR_USUARIO, (id_usuario,))
        rows = cursor.fetchall()
        return [
            Endereco(
                id_endereco=row["id_endereco"],
                id_usuario=row["id_usuario"],
                titulo=row["titulo"],
                logradouro=row["logradouro"],
                numero=row["numero"],
                complemento=row["complemento"],
                bairro=row["bairro"],
                cidade=row["cidade"],
                uf=row["uf"],
                cep=row["cep"],
                usuario=None
            )
            for row in rows
        ]


def obter_todos() -> list[Endereco]:
    """Obtém todos os endereços"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [
            Endereco(
                id_endereco=row["id_endereco"],
                id_usuario=row["id_usuario"],
                titulo=row["titulo"],
                logradouro=row["logradouro"],
                numero=row["numero"],
                complemento=row["complemento"],
                bairro=row["bairro"],
                cidade=row["cidade"],
                uf=row["uf"],
                cep=row["cep"],
                usuario=None
            )
            for row in rows
        ]
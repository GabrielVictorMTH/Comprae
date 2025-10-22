"""
Repositório para operações com mensagens.
"""
from typing import Optional
from datetime import datetime

from model.mensagem_model import Mensagem
from sql.mensagem_sql import *
from util.db_util import get_connection


def criar_tabela() -> bool:
    """Cria a tabela de mensagens e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICE_REMETENTE)
        cursor.execute(CRIAR_INDICE_DESTINATARIO)
        return True


def inserir(mensagem: Mensagem) -> Optional[Mensagem]:
    """Insere uma nova mensagem"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (mensagem.id_remetente, mensagem.id_destinatario, mensagem.mensagem)
        )
        if cursor.lastrowid:
            return obter_por_id(cursor.lastrowid)
        return None


def marcar_como_lida(id_mensagem: int) -> bool:
    """Marca uma mensagem como lida"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_COMO_LIDA, (id_mensagem,))
        return cursor.rowcount > 0


def obter_por_id(id_mensagem: int) -> Optional[Mensagem]:
    """Obtém uma mensagem por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_mensagem,))
        row = cursor.fetchone()
        if row:
            return Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
        return None


def obter_conversa(id_usuario1: int, id_usuario2: int) -> list[Mensagem]:
    """Obtém todas as mensagens entre dois usuários"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_CONVERSA, (id_usuario1, id_usuario2, id_usuario2, id_usuario1))
        rows = cursor.fetchall()
        return [
            Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
            for row in rows
        ]


def obter_mensagens_recebidas(id_usuario: int) -> list[Mensagem]:
    """Obtém todas as mensagens recebidas por um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_MENSAGENS_RECEBIDAS, (id_usuario,))
        rows = cursor.fetchall()
        return [
            Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
            for row in rows
        ]


def obter_mensagens_nao_lidas(id_usuario: int) -> list[Mensagem]:
    """Obtém mensagens não lidas de um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_MENSAGENS_NAO_LIDAS, (id_usuario,))
        rows = cursor.fetchall()
        return [
            Mensagem(
                id_mensagem=row["id_mensagem"],
                id_remetente=row["id_remetente"],
                id_destinatario=row["id_destinatario"],
                mensagem=row["mensagem"],
                data_hora=datetime.fromisoformat(row["data_hora"]),
                visualizada=bool(row["visualizada"]),
                remetente=None,
                destinatario=None
            )
            for row in rows
        ]


def contar_nao_lidas(id_usuario: int) -> int:
    """Conta mensagens não lidas de um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS, (id_usuario,))
        row = cursor.fetchone()
        return row["total"] if row else 0
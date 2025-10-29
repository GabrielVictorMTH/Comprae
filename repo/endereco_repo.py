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
            endereco.id
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
                id=row["id"],
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
                id=row["id"],
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
                id=row["id"],
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


def obter_por_uf(uf: str) -> list[Endereco]:
    """Obtém endereços por UF"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM endereco WHERE uf = ? ORDER BY cidade, logradouro", (uf,))
        rows = cursor.fetchall()
        return [
            Endereco(
                id=row["id"],
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


def obter_estatisticas() -> dict:
    """Obtém estatísticas de endereços"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Total de endereços
        cursor.execute("SELECT COUNT(*) as total FROM endereco")
        total = cursor.fetchone()["total"]

        # Total de usuários com endereço
        cursor.execute("SELECT COUNT(DISTINCT id_usuario) as total FROM endereco")
        usuarios_com_endereco = cursor.fetchone()["total"]

        # Média de endereços por usuário
        media = total / usuarios_com_endereco if usuarios_com_endereco > 0 else 0

        return {
            "total_enderecos": total,
            "usuarios_com_endereco": usuarios_com_endereco,
            "media_enderecos_por_usuario": round(media, 2)
        }


def contar_por_uf() -> list[dict]:
    """Conta endereços por UF"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT uf, COUNT(*) as total
            FROM endereco
            GROUP BY uf
            ORDER BY total DESC, uf
        """)
        rows = cursor.fetchall()
        return [{"uf": row["uf"], "total": row["total"]} for row in rows]


def contar_por_cidade() -> list[dict]:
    """Conta endereços por cidade (top 10)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cidade, uf, COUNT(*) as total
            FROM endereco
            GROUP BY cidade, uf
            ORDER BY total DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        return [
            {
                "cidade": row["cidade"],
                "uf": row["uf"],
                "total": row["total"]
            }
            for row in rows
        ]


def obter_duplicados() -> list[dict]:
    """Detecta endereços potencialmente duplicados (mesmo CEP + número)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                cep,
                numero,
                logradouro,
                bairro,
                cidade,
                uf,
                COUNT(*) as total_usuarios,
                GROUP_CONCAT(id_usuario) as usuarios_ids
            FROM endereco
            GROUP BY cep, numero
            HAVING COUNT(*) > 1
            ORDER BY total_usuarios DESC, cidade
        """)
        rows = cursor.fetchall()

        duplicados = []
        for row in rows:
            # Buscar detalhes dos endereços duplicados
            ids_usuarios = row["usuarios_ids"].split(",")
            cursor.execute(f"""
                SELECT e.*, u.nome as nome_usuario, u.email as email_usuario
                FROM endereco e
                JOIN usuario u ON e.id_usuario = u.id
                WHERE e.cep = ? AND e.numero = ?
                ORDER BY e.id_usuario
            """, (row["cep"], row["numero"]))
            enderecos = cursor.fetchall()

            duplicados.append({
                "cep": row["cep"],
                "numero": row["numero"],
                "logradouro": row["logradouro"],
                "bairro": row["bairro"],
                "cidade": row["cidade"],
                "uf": row["uf"],
                "total_usuarios": row["total_usuarios"],
                "enderecos": [
                    {
                        "id": e["id"],
                        "titulo": e["titulo"],
                        "complemento": e["complemento"],
                        "id_usuario": e["id_usuario"],
                        "nome_usuario": e["nome_usuario"],
                        "email_usuario": e["email_usuario"]
                    }
                    for e in enderecos
                ]
            })

        return duplicados
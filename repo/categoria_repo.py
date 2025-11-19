from typing import Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import get_connection

def criar_tabela():
    """
    Cria a tabela de categorias se ela não existir.
    Deve ser chamada na inicialização do sistema.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(categoria: Categoria) -> Optional[Categoria]:
    """
    Insere uma nova categoria no banco de dados.

    Args:
        categoria: Objeto Categoria com nome e descrição

    Returns:
        Categoria com ID preenchido se sucesso, None se erro

    Exemplo:
        nova = Categoria(nome="Esportes", descricao="Notícias esportivas")
        resultado = inserir(nova)
        if resultado:
            print(f"Categoria criada com ID: {resultado.id}")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (categoria.nome, categoria.descricao))

            # Pega o ID gerado automaticamente
            if cursor.lastrowid:
                categoria.id = cursor.lastrowid
                return categoria
            return None
    except Exception as e:
        print(f"Erro ao inserir categoria: {e}")
        return None


def alterar(categoria: Categoria) -> bool:
    """
    Atualiza uma categoria existente.

    Args:
        categoria: Objeto Categoria com ID, nome e descrição

    Returns:
        True se atualizou, False se erro

    Exemplo:
        cat = obter_por_id(5)
        cat.nome = "Novo Nome"
        if alterar(cat):
            print("Categoria atualizada!")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                ALTERAR,
                (categoria.nome, categoria.descricao, categoria.id)
            )
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar categoria: {e}")
        return False


def excluir(id: int) -> bool:
    """
    Exclui uma categoria do banco de dados.

    Args:
        id: ID da categoria a ser excluída

    Returns:
        True se excluiu, False se erro ou não encontrou

    Exemplo:
        if excluir(5):
            print("Categoria excluída!")
        else:
            print("Categoria não encontrada")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(EXCLUIR, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir categoria: {e}")
        return False


def obter_por_id(id: int) -> Optional[Categoria]:
    """
    Busca uma categoria por ID.

    Args:
        id: ID da categoria

    Returns:
        Objeto Categoria se encontrou, None se não encontrou

    Exemplo:
        cat = obter_por_id(5)
        if cat:
            print(f"Encontrada: {cat.nome}")
        else:
            print("Categoria não existe")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_ID, (id,))
            row = cursor.fetchone()

            if row:
                return Categoria(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por ID: {e}")
        return None


def obter_todos() -> list[Categoria]:
    """
    Retorna todas as categorias do banco de dados.

    Returns:
        Lista de objetos Categoria (pode ser vazia)

    Exemplo:
        categorias = obter_todos()
        for cat in categorias:
            print(f"{cat.id} - {cat.nome}")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_TODOS)
            rows = cursor.fetchall()

            return [
                Categoria(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
                for row in rows
            ]
    except Exception as e:
        print(f"Erro ao obter todas as categorias: {e}")
        return []


def obter_por_nome(nome: str) -> Optional[Categoria]:
    """
    Busca uma categoria pelo nome exato.
    Útil para verificar se já existe categoria com aquele nome.

    Args:
        nome: Nome da categoria (case-sensitive)

    Returns:
        Objeto Categoria se encontrou, None se não encontrou

    Exemplo:
        if obter_por_nome("Tecnologia"):
            print("Já existe categoria com este nome")
        else:
            print("Nome disponível")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_NOME, (nome,))
            row = cursor.fetchone()

            if row:
                return Categoria(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por nome: {e}")
        return None
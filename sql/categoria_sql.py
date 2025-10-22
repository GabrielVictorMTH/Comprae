CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL
)
"""

INSERIR = "INSERT INTO categoria (nome, descricao) VALUES (?, ?)"
ALTERAR = "UPDATE categoria SET nome = ?, descricao = ? WHERE id = ?"
EXCLUIR = "DELETE FROM categoria WHERE id = ?"
OBTER_POR_ID = "SELECT * FROM categoria WHERE id = ?"
OBTER_TODOS = "SELECT * FROM categoria ORDER BY nome"
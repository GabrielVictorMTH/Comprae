CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS tarefa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    concluida INTEGER DEFAULT 0,
    usuario_id INTEGER NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_conclusao TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO tarefa (titulo, descricao, usuario_id)
VALUES (?, ?, ?)
"""

OBTER_TODOS_POR_USUARIO = """
SELECT * FROM tarefa
WHERE usuario_id = ?
ORDER BY concluida ASC, data_criacao DESC
"""

OBTER_POR_ID = "SELECT * FROM tarefa WHERE id = ?"

ATUALIZAR = """
UPDATE tarefa
SET titulo = ?, descricao = ?, concluida = ?
WHERE id = ?
"""

MARCAR_CONCLUIDA = """
UPDATE tarefa
SET concluida = 1, data_conclusao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = "DELETE FROM tarefa WHERE id = ?"

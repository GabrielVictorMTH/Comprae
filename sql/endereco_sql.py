"""
Queries SQL para tabela de Endereços.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS endereco (
    id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    logradouro TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    cep TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

# Índice para otimizar buscas por usuário
CRIAR_INDICE = """
CREATE INDEX IF NOT EXISTS idx_endereco_usuario
ON endereco(id_usuario)
"""

INSERIR = """
INSERT INTO endereco (id_usuario, titulo, logradouro, numero, complemento, bairro, cidade, uf, cep)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

ALTERAR = """
UPDATE endereco
SET titulo = ?, logradouro = ?, numero = ?, complemento = ?,
    bairro = ?, cidade = ?, uf = ?, cep = ?
WHERE id_endereco = ?
"""

EXCLUIR = """
DELETE FROM endereco
WHERE id_endereco = ?
"""

OBTER_POR_ID = """
SELECT * FROM endereco
WHERE id_endereco = ?
"""

OBTER_TODOS_POR_USUARIO = """
SELECT * FROM endereco
WHERE id_usuario = ?
ORDER BY titulo
"""

OBTER_TODOS = """
SELECT * FROM endereco
ORDER BY id_usuario, titulo
"""
"""
Queries SQL para tabela de Anúncios (Produtos).
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS anuncio (
    id_anuncio INTEGER PRIMARY KEY AUTOINCREMENT,
    id_vendedor INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    peso REAL NOT NULL,
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (id_vendedor) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE RESTRICT
)
"""

# Índices para otimizar buscas
CRIAR_INDICE_VENDEDOR = """
CREATE INDEX IF NOT EXISTS idx_anuncio_vendedor
ON anuncio(id_vendedor)
"""

CRIAR_INDICE_CATEGORIA = """
CREATE INDEX IF NOT EXISTS idx_anuncio_categoria
ON anuncio(id_categoria)
"""

CRIAR_INDICE_ATIVO = """
CREATE INDEX IF NOT EXISTS idx_anuncio_ativo
ON anuncio(ativo)
"""

INSERIR = """
INSERT INTO anuncio (id_vendedor, id_categoria, nome, descricao, peso, preco, estoque)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

ALTERAR = """
UPDATE anuncio
SET id_categoria = ?, nome = ?, descricao = ?, peso = ?, preco = ?, estoque = ?, ativo = ?
WHERE id_anuncio = ?
"""

EXCLUIR = """
DELETE FROM anuncio
WHERE id_anuncio = ?
"""

OBTER_POR_ID = """
SELECT * FROM anuncio
WHERE id_anuncio = ?
"""

OBTER_TODOS = """
SELECT * FROM anuncio
ORDER BY data_cadastro DESC
"""

OBTER_TODOS_ATIVOS = """
SELECT * FROM anuncio
WHERE ativo = 1 AND estoque > 0
ORDER BY data_cadastro DESC
"""

OBTER_POR_VENDEDOR = """
SELECT * FROM anuncio
WHERE id_vendedor = ?
ORDER BY data_cadastro DESC
"""

OBTER_POR_CATEGORIA = """
SELECT * FROM anuncio
WHERE id_categoria = ? AND ativo = 1 AND estoque > 0
ORDER BY data_cadastro DESC
"""

BUSCAR_POR_NOME = """
SELECT * FROM anuncio
WHERE nome LIKE ? AND ativo = 1 AND estoque > 0
ORDER BY data_cadastro DESC
"""

BUSCAR_COM_FILTROS = """
SELECT * FROM anuncio
WHERE ativo = 1 AND estoque > 0
  AND (? IS NULL OR nome LIKE ?)
  AND (? IS NULL OR id_categoria = ?)
  AND (? IS NULL OR preco >= ?)
  AND (? IS NULL OR preco <= ?)
ORDER BY data_cadastro DESC
"""

ATUALIZAR_ESTOQUE = """
UPDATE anuncio
SET estoque = estoque - ?
WHERE id_anuncio = ? AND estoque >= ?
"""
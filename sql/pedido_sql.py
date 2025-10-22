"""
Queries SQL para tabela de Pedidos.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS pedido (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    id_endereco INTEGER NOT NULL,
    id_comprador INTEGER NOT NULL,
    id_anuncio INTEGER NOT NULL,
    preco REAL NOT NULL,
    status TEXT DEFAULT 'Pendente',
    data_hora_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_hora_pagamento DATETIME,
    data_hora_envio DATETIME,
    codigo_rastreio TEXT,
    nota_avaliacao INTEGER,
    comentario_avaliacao TEXT,
    data_hora_avaliacao DATETIME,
    FOREIGN KEY (id_endereco) REFERENCES endereco(id_endereco) ON DELETE RESTRICT,
    FOREIGN KEY (id_comprador) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_anuncio) REFERENCES anuncio(id_anuncio) ON DELETE RESTRICT,
    CHECK (nota_avaliacao IS NULL OR (nota_avaliacao >= 1 AND nota_avaliacao <= 5))
)
"""

# Índices para otimizar buscas
CRIAR_INDICE_COMPRADOR = """
CREATE INDEX IF NOT EXISTS idx_pedido_comprador
ON pedido(id_comprador)
"""

CRIAR_INDICE_ANUNCIO = """
CREATE INDEX IF NOT EXISTS idx_pedido_anuncio
ON pedido(id_anuncio)
"""

CRIAR_INDICE_STATUS = """
CREATE INDEX IF NOT EXISTS idx_pedido_status
ON pedido(status)
"""

INSERIR = """
INSERT INTO pedido (id_endereco, id_comprador, id_anuncio, preco, status)
VALUES (?, ?, ?, ?, 'Pendente')
"""

ATUALIZAR_STATUS = """
UPDATE pedido
SET status = ?
WHERE id_pedido = ?
"""

ATUALIZAR_PARA_PAGO = """
UPDATE pedido
SET status = 'Pago', data_hora_pagamento = CURRENT_TIMESTAMP
WHERE id_pedido = ?
"""

ATUALIZAR_PARA_ENVIADO = """
UPDATE pedido
SET status = 'Enviado', data_hora_envio = CURRENT_TIMESTAMP, codigo_rastreio = ?
WHERE id_pedido = ?
"""

CANCELAR_PEDIDO = """
UPDATE pedido
SET status = 'Cancelado'
WHERE id_pedido = ?
"""

AVALIAR_PEDIDO = """
UPDATE pedido
SET nota_avaliacao = ?, comentario_avaliacao = ?, data_hora_avaliacao = CURRENT_TIMESTAMP
WHERE id_pedido = ?
"""

OBTER_POR_ID = """
SELECT * FROM pedido
WHERE id_pedido = ?
"""

OBTER_POR_COMPRADOR = """
SELECT * FROM pedido
WHERE id_comprador = ?
ORDER BY data_hora_pedido DESC
"""

OBTER_POR_VENDEDOR = """
SELECT p.* FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id_anuncio
WHERE a.id_vendedor = ?
ORDER BY p.data_hora_pedido DESC
"""

OBTER_POR_STATUS = """
SELECT * FROM pedido
WHERE status = ?
ORDER BY data_hora_pedido DESC
"""

OBTER_TODOS = """
SELECT * FROM pedido
ORDER BY data_hora_pedido DESC
"""

OBTER_COM_DETALHES = """
SELECT
    p.*,
    a.nome as nome_produto,
    a.id_vendedor,
    u_comprador.nome as nome_comprador,
    u_comprador.email as email_comprador,
    e.logradouro, e.numero, e.cidade, e.uf
FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id_anuncio
INNER JOIN usuario u_comprador ON p.id_comprador = u_comprador.id
INNER JOIN endereco e ON p.id_endereco = e.id_endereco
WHERE p.id_pedido = ?
"""
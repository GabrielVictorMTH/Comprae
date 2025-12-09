"""
Queries SQL para tabela de Pedidos.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    FOREIGN KEY (id_endereco) REFERENCES endereco(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_comprador) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_anuncio) REFERENCES anuncio(id) ON DELETE RESTRICT,
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
VALUES (?, ?, ?, ?, 'Negociando')
"""

INSERIR_NEGOCIANDO = """
INSERT INTO pedido (id_endereco, id_comprador, id_anuncio, preco, status)
VALUES (?, ?, ?, 0, 'Negociando')
"""

DEFINIR_PRECO_FINAL = """
UPDATE pedido
SET preco = ?, status = 'Pendente'
WHERE id = ? AND status = 'Negociando'
"""

ATUALIZAR_PARA_ENTREGUE = """
UPDATE pedido
SET status = 'Entregue'
WHERE id = ? AND status = 'Enviado'
"""

ATUALIZAR_STATUS = """
UPDATE pedido
SET status = ?
WHERE id = ?
"""

ATUALIZAR_PARA_PAGO = """
UPDATE pedido
SET status = 'Pago', data_hora_pagamento = CURRENT_TIMESTAMP
WHERE id = ?
"""

ATUALIZAR_PARA_ENVIADO = """
UPDATE pedido
SET status = 'Enviado', data_hora_envio = CURRENT_TIMESTAMP, codigo_rastreio = ?
WHERE id = ?
"""

CANCELAR_PEDIDO = """
UPDATE pedido
SET status = 'Cancelado'
WHERE id = ?
"""

AVALIAR_PEDIDO = """
UPDATE pedido
SET nota_avaliacao = ?, comentario_avaliacao = ?, data_hora_avaliacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

OBTER_POR_ID = """
SELECT * FROM pedido
WHERE id = ?
"""

OBTER_POR_COMPRADOR = """
SELECT * FROM pedido
WHERE id_comprador = ?
ORDER BY data_hora_pedido DESC
"""

OBTER_POR_VENDEDOR = """
SELECT p.* FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id
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
    a.preco as preco_anuncio,
    u_comprador.nome as nome_comprador,
    u_comprador.email as email_comprador,
    u_vendedor.nome as nome_vendedor,
    e.logradouro, e.numero, e.complemento, e.bairro, e.cidade, e.uf, e.cep
FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id
INNER JOIN usuario u_comprador ON p.id_comprador = u_comprador.id
INNER JOIN usuario u_vendedor ON a.id_vendedor = u_vendedor.id
INNER JOIN endereco e ON p.id_endereco = e.id
WHERE p.id = ?
"""

OBTER_POR_COMPRADOR_COM_DETALHES = """
SELECT
    p.*,
    a.nome as nome_produto,
    a.id_vendedor,
    u_vendedor.nome as nome_vendedor
FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id
INNER JOIN usuario u_vendedor ON a.id_vendedor = u_vendedor.id
WHERE p.id_comprador = ?
ORDER BY p.data_hora_pedido DESC
"""

OBTER_POR_VENDEDOR_COM_DETALHES = """
SELECT
    p.*,
    a.nome as nome_produto,
    a.id_vendedor,
    u_comprador.nome as nome_comprador
FROM pedido p
INNER JOIN anuncio a ON p.id_anuncio = a.id
INNER JOIN usuario u_comprador ON p.id_comprador = u_comprador.id
WHERE a.id_vendedor = ?
ORDER BY p.data_hora_pedido DESC
"""
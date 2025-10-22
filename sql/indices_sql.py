"""
Índices do banco de dados para otimização de performance

SQLite automaticamente cria índices para:
- PRIMARY KEY
- UNIQUE constraints

Estes índices adicionais otimizam queries frequentes.
"""

# Índices da tabela usuario
CRIAR_INDICE_USUARIO_PERFIL = """
CREATE INDEX IF NOT EXISTS idx_usuario_perfil
ON usuario(perfil)
"""

CRIAR_INDICE_USUARIO_TOKEN = """
CREATE INDEX IF NOT EXISTS idx_usuario_token
ON usuario(token_redefinicao)
WHERE token_redefinicao IS NOT NULL
"""

# Índices da tabela tarefa
CRIAR_INDICE_TAREFA_USUARIO = """
CREATE INDEX IF NOT EXISTS idx_tarefa_usuario
ON tarefa(usuario_id)
"""

CRIAR_INDICE_TAREFA_USUARIO_CONCLUIDA = """
CREATE INDEX IF NOT EXISTS idx_tarefa_usuario_concluida
ON tarefa(usuario_id, concluida, data_criacao DESC)
"""

# Índices da tabela endereco
CRIAR_INDICE_ENDERECO_USUARIO = """
CREATE INDEX IF NOT EXISTS idx_endereco_usuario
ON endereco(id_usuario)
"""

# Índices da tabela anuncio
CRIAR_INDICE_ANUNCIO_VENDEDOR = """
CREATE INDEX IF NOT EXISTS idx_anuncio_vendedor
ON anuncio(id_vendedor)
"""

CRIAR_INDICE_ANUNCIO_CATEGORIA = """
CREATE INDEX IF NOT EXISTS idx_anuncio_categoria
ON anuncio(id_categoria)
"""

CRIAR_INDICE_ANUNCIO_ATIVO = """
CREATE INDEX IF NOT EXISTS idx_anuncio_ativo
ON anuncio(ativo)
"""

# Índices da tabela pedido
CRIAR_INDICE_PEDIDO_COMPRADOR = """
CREATE INDEX IF NOT EXISTS idx_pedido_comprador
ON pedido(id_comprador)
"""

CRIAR_INDICE_PEDIDO_ANUNCIO = """
CREATE INDEX IF NOT EXISTS idx_pedido_anuncio
ON pedido(id_anuncio)
"""

CRIAR_INDICE_PEDIDO_STATUS = """
CREATE INDEX IF NOT EXISTS idx_pedido_status
ON pedido(status)
"""

# Lista de todos os índices para criação
TODOS_INDICES = [
    # Upstream
    CRIAR_INDICE_USUARIO_PERFIL,
    CRIAR_INDICE_USUARIO_TOKEN,
    CRIAR_INDICE_TAREFA_USUARIO,
    CRIAR_INDICE_TAREFA_USUARIO_CONCLUIDA,
    # Compraê - Endereços
    CRIAR_INDICE_ENDERECO_USUARIO,
    # Compraê - Anúncios
    CRIAR_INDICE_ANUNCIO_VENDEDOR,
    CRIAR_INDICE_ANUNCIO_CATEGORIA,
    CRIAR_INDICE_ANUNCIO_ATIVO,
    # Compraê - Pedidos
    CRIAR_INDICE_PEDIDO_COMPRADOR,
    CRIAR_INDICE_PEDIDO_ANUNCIO,
    CRIAR_INDICE_PEDIDO_STATUS,
]

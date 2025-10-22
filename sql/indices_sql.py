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

# Lista de todos os índices para criação
TODOS_INDICES = [
    CRIAR_INDICE_USUARIO_PERFIL,
    CRIAR_INDICE_USUARIO_TOKEN,
    CRIAR_INDICE_TAREFA_USUARIO,
    CRIAR_INDICE_TAREFA_USUARIO_CONCLUIDA,
]

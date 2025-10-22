"""
Queries SQL para tabela de Mensagens.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS mensagem (
    id_mensagem INTEGER PRIMARY KEY AUTOINCREMENT,
    id_remetente INTEGER NOT NULL,
    id_destinatario INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    visualizada BOOLEAN DEFAULT 0,
    FOREIGN KEY (id_remetente) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_destinatario) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

# Índices para otimizar buscas por remetente e destinatário
CRIAR_INDICE_REMETENTE = """
CREATE INDEX IF NOT EXISTS idx_mensagem_remetente
ON mensagem(id_remetente)
"""

CRIAR_INDICE_DESTINATARIO = """
CREATE INDEX IF NOT EXISTS idx_mensagem_destinatario
ON mensagem(id_destinatario)
"""

INSERIR = """
INSERT INTO mensagem (id_remetente, id_destinatario, mensagem)
VALUES (?, ?, ?)
"""

MARCAR_COMO_LIDA = """
UPDATE mensagem
SET visualizada = 1
WHERE id_mensagem = ?
"""

OBTER_POR_ID = """
SELECT * FROM mensagem
WHERE id_mensagem = ?
"""

OBTER_CONVERSA = """
SELECT * FROM mensagem
WHERE (id_remetente = ? AND id_destinatario = ?)
   OR (id_remetente = ? AND id_destinatario = ?)
ORDER BY data_hora ASC
"""

OBTER_MENSAGENS_RECEBIDAS = """
SELECT * FROM mensagem
WHERE id_destinatario = ?
ORDER BY data_hora DESC
"""

OBTER_MENSAGENS_NAO_LIDAS = """
SELECT * FROM mensagem
WHERE id_destinatario = ? AND visualizada = 0
ORDER BY data_hora DESC
"""

CONTAR_NAO_LIDAS = """
SELECT COUNT(*) as total
FROM mensagem
WHERE id_destinatario = ? AND visualizada = 0
"""
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS curtida (
    id_usuario INTEGER NOT NULL,
    id_anuncio INTEGER NOT NULL,
    data_curtida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_anuncio),
    FOREIGN KEY (id_usuario) REFERENCES usuario (id),
    FOREIGN KEY (id_anuncio) REFERENCES anuncio (id)
)
"""

INSERIR = "INSERT INTO curtida (id_usuario, id_anuncio) VALUES (?, ?)"
EXCLUIR = "DELETE FROM curtida WHERE id_usuario = ? AND id_anuncio = ?"
OBTER_POR_ID = "SELECT * FROM curtida WHERE id_usuario = ? AND id_anuncio = ?"
OBTER_QUANTIDADE_POR_ANUNCIO = "SELECT COUNT (*) AS quantidade FROM curtida ORDER BY data_curtida DESC"
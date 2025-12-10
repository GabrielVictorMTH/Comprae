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
OBTER_TODOS = "SELECT * FROM curtida ORDER BY data_curtida DESC"


OBTER_POR_USUARIO = """
SELECT c.*, a.nome as nome_anuncio, a.preco, a.descricao, a.estoque,
       cat.nome as nome_categoria
FROM curtida c
INNER JOIN anuncio a ON c.id_anuncio = a.id
LEFT JOIN categoria cat ON a.id_categoria = cat.id
WHERE c.id_usuario = ? AND a.ativo = 1
ORDER BY c.data_curtida DESC
"""

CONTAR_POR_USUARIO = """
SELECT COUNT(*) as quantidade
FROM curtida
WHERE id_usuario = ?
"""
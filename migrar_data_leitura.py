"""
Script de migração para adicionar coluna data_leitura na tabela chamado_interacao.

Este script verifica se a coluna já existe antes de tentar adicionar.
É seguro executar múltiplas vezes.

Uso:
    python migrar_data_leitura.py
"""

import sqlite3
from util.config import DATABASE_PATH
from util.logger_config import logger


def coluna_existe(cursor, tabela: str, coluna: str) -> bool:
    """Verifica se uma coluna existe em uma tabela."""
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [row[1] for row in cursor.fetchall()]
    return coluna in colunas


def adicionar_coluna_data_leitura():
    """Adiciona a coluna data_leitura à tabela chamado_interacao."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Verificar se a coluna já existe
        if coluna_existe(cursor, 'chamado_interacao', 'data_leitura'):
            logger.info("✓ Coluna 'data_leitura' já existe na tabela 'chamado_interacao'")
            print("✓ Migração já foi aplicada anteriormente. Nada a fazer.")
            return

        # Adicionar a coluna
        logger.info("Adicionando coluna 'data_leitura' à tabela 'chamado_interacao'...")
        cursor.execute("""
            ALTER TABLE chamado_interacao
            ADD COLUMN data_leitura TIMESTAMP
        """)

        conn.commit()
        logger.info("✓ Coluna 'data_leitura' adicionada com sucesso!")
        print("✓ Migração aplicada com sucesso!")
        print("  - Coluna 'data_leitura' adicionada à tabela 'chamado_interacao'")

    except sqlite3.Error as e:
        logger.error(f"Erro ao executar migração: {e}")
        print(f"✗ Erro ao executar migração: {e}")
        raise
    finally:
        if conn:
            conn.close()


def verificar_integridade():
    """Verifica a integridade do banco após a migração."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Verificar se a coluna foi adicionada
        if not coluna_existe(cursor, 'chamado_interacao', 'data_leitura'):
            raise Exception("Coluna 'data_leitura' não foi encontrada após migração")

        # Contar registros na tabela
        cursor.execute("SELECT COUNT(*) FROM chamado_interacao")
        total = cursor.fetchone()[0]

        logger.info(f"✓ Verificação de integridade passou: {total} registros na tabela")
        print(f"✓ Verificação de integridade passou: {total} registros existentes")

    except Exception as e:
        logger.error(f"Erro na verificação de integridade: {e}")
        print(f"✗ Erro na verificação de integridade: {e}")
        raise
    finally:
        if conn:
            conn.close()


def main():
    """Função principal do script de migração."""
    print("=" * 60)
    print("Migração: Adicionar coluna data_leitura")
    print("=" * 60)
    print()

    try:
        # Executar migração
        adicionar_coluna_data_leitura()
        print()

        # Verificar integridade
        print("Verificando integridade do banco de dados...")
        verificar_integridade()
        print()

        print("=" * 60)
        print("Migração concluída com sucesso!")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print("ERRO: Migração falhou!")
        print("=" * 60)
        logger.error(f"Migração falhou: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

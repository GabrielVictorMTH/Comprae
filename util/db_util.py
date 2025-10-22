import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

@contextmanager
def get_connection():
    """Context manager para conexão com banco de dados"""
    register_adapters()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def adapt_datetime(dt: datetime) -> str:
    """Adaptador para converter datetime para string ISO"""
    return dt.isoformat()


def convert_datetime(s: bytes) -> datetime:
    """Conversor para converter string ISO de volta para datetime"""
    return datetime.fromisoformat(s.decode())


def register_adapters() -> None:
    """Registra os adaptadores customizados para datetime no sqlite3"""
    sqlite3.register_adapter(datetime, adapt_datetime)
    sqlite3.register_converter("TIMESTAMP", convert_datetime)
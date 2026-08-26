"""
Camada Centralizada de Conexão com o Banco de Dados (database/connection.py).
Gerencia conexões com suporte duplo transparente:
- SQLCipher (banco criptografado app.db)
- SQLite padrão (dka_ferramentas.db exportado do MySQL)
"""
import os
import sys
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
try:
    from sqlcipher3 import dbapi2 as sqlcipher3_dbapi
    HAS_SQLCIPHER = True
except ImportError:
    import sqlite3 as sqlcipher3_dbapi
    HAS_SQLCIPHER = False

from app.config.database import get_database_path, derive_encryption_key

_engine = None
_SessionFactory = None

class DatabaseError(Exception):
    """Exceção customizada para erros de conexão ou criptografia do banco de dados."""
    pass

def init_engine(db_path=None, secret_key=None):
    """Inicializa a engine do SQLAlchemy com detecção automática do tipo de banco (SQLCipher ou SQLite Padrão)."""
    global _engine, _SessionFactory

    path = str(db_path) if db_path else str(get_database_path())
    key = secret_key if secret_key is not None else derive_encryption_key()

    def dbapi_creator():
        # Verifica se o arquivo inicia com o cabeçalho mágico do SQLite padrão (unencrypted)
        is_plain_sqlite = False
        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    header = f.read(16)
                    if header == b"SQLite format 3\x00":
                        is_plain_sqlite = True
        except Exception:
            pass

        conn = sqlcipher3_dbapi.connect(path)
        if HAS_SQLCIPHER and not is_plain_sqlite:
            # Aplicação da chave de criptografia SQLCipher apenas para bancos criptografados
            conn.execute(f"PRAGMA key = '{key}'")
        return conn

    _engine = create_engine("sqlite://", creator=dbapi_creator, pool_pre_ping=True)
    _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine

def get_engine():
    """Retorna a instância global da Engine do SQLAlchemy."""
    global _engine
    if _engine is None:
        init_engine()
    return _engine

def validate_connection() -> bool:
    """
    Valida se a estrutura do banco é acessível.
    Lança DatabaseError tratado se o banco estiver inacessível ou corrompido.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT count(*) FROM sqlite_master;"))
        return True
    except Exception as e:
        raise DatabaseError(
            "Falha ao acessar o banco de dados. "
            "O arquivo pode estar corrompido ou inacessível."
        ) from None

def get_session() -> Session:
    """Retorna uma nova sessão gerenciada do SQLAlchemy."""
    global _SessionFactory
    if _SessionFactory is None:
        get_engine()
    return _SessionFactory()

def close_connection():
    """Fecha adequadamente o pool de conexões com o banco de dados."""
    global _engine, _SessionFactory
    if _engine:
        _engine.dispose()
        _engine = None
        _SessionFactory = None

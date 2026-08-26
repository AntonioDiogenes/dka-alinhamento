"""
Configurações de Banco de Dados Criptografado com SQLCipher / SQLite (config/database.py).
Define a localização do arquivo .db (dka_ferramentas.db ou app.db).
"""
import os
import sys
import hashlib
from pathlib import Path

# Alternar para True se quiser usar o dka_ferramentas.db (MySQL) ou False para app.db (Banco Antigo Local)
USE_MYSQL_EXPORTED_DB = False

def get_database_dir() -> Path:
    """
    Retorna o diretório persistente adequado para armazenamento do banco de dados local.
    Garante compatibilidade com empacotamento PyInstaller (não salva em diretórios temporários _MEIPASS).
    """
    if getattr(sys, 'frozen', False):
        # Executável empacotado via PyInstaller
        base_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".dka_tkinter"))
    else:
        # Modo de desenvolvimento local
        base_dir = Path(__file__).resolve().parent.parent.parent / "database"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_database_path() -> Path:
    """
    Retorna o caminho completo para o arquivo de banco de dados.
    Mudar a flag USE_MYSQL_EXPORTED_DB = True/False para alternar entre bancos.
    """
    db_dir = get_database_dir()
    
    if USE_MYSQL_EXPORTED_DB:
        # 1. Tenta dka_ferramentas.db no diretório database/
        dka_db = db_dir / "dka_ferramentas.db"
        if dka_db.exists():
            return dka_db

        # 2. Tenta dka_ferramentas.db na raiz da aplicação
        root_dka_db = db_dir.parent / "dka_ferramentas.db"
        if root_dka_db.exists():
            return root_dka_db

    # Retorna o banco antigo app.db por padrão
    return db_dir / "app.db"

def derive_encryption_key() -> str:
    """
    Gera/deriva a chave de criptografia para o SQLCipher.
    """
    part1 = b"DKA_OFICINA_SECURE_KEY_2026"
    part2 = b"ALINHAMENTO_TRUCK_SQLCIPHER"
    seed = hashlib.pbkdf2_hmac('sha256', part1, part2, 10000)
    return seed.hex()

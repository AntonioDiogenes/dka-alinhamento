"""
Suíte de Testes Automatizados de Persistência e Segurança com SQLCipher (tests/test_database.py).
Cobre os 5 testes obrigatórios especificados:
1. Teste 1 — Banco Criptografado (impede abertura via sqlite3 convencional)
2. Teste 2 — Chave Correta (autenticação com sucesso)
3. Teste 3 — Chave Incorreta (falha ao tentar acessar com senha errada)
4. Teste 4 — Operações CRUD completas via Repository/Service
5. Teste 5 — Persistência entre reinicializações do sistema
"""
import os
import unittest
import sqlite3 as std_sqlite3
from pathlib import Path
try:
    from sqlcipher3 import dbapi2 as sqlcipher3_dbapi
    HAS_SQLCIPHER = True
except (ImportError, Exception):
    import sqlite3 as sqlcipher3_dbapi
    HAS_SQLCIPHER = False

from app.config.database import derive_encryption_key
from app.database.connection import init_engine, close_connection, get_session
from app.database.migrations import run_migrations
from app.database.repositories.client_repository import ClientRepository
from app.services.client_service import ClientService

TEST_DB_PATH = Path(__file__).resolve().parent / "test_encrypted_app.db"

class TestDatabaseSecurityAndPersistence(unittest.TestCase):

    def setUp(self):
        """Limpa banco temporário de teste antes de cada caso."""
        close_connection()
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)
        
        # Inicializa e popula o banco criptografado de teste
        init_engine(db_path=TEST_DB_PATH)
        run_migrations()

    def tearDown(self):
        """Encerra conexões e remove o banco temporário."""
        close_connection()
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)

    @unittest.skipUnless(HAS_SQLCIPHER, "SQLCipher não disponível neste ambiente")
    def test_1_banco_criptografado(self):
        """Teste 1: Verifica que o arquivo NÃO pode ser lido por clientes SQLite normais sem a chave."""
        close_connection()
        self.assertTrue(TEST_DB_PATH.exists(), "O arquivo do banco deve existir na pasta de dados.")

        with self.assertRaises(std_sqlite3.DatabaseError):
            conn = std_sqlite3.connect(str(TEST_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sqlite_master;")
            cursor.fetchall()
            conn.close()

    @unittest.skipUnless(HAS_SQLCIPHER, "SQLCipher não disponível neste ambiente")
    def test_2_chave_correta(self):
        """Teste 2: A aplicação consegue abrir e consultar o banco usando a chave correta."""
        close_connection()
        key = derive_encryption_key()

        conn = sqlcipher3_dbapi.connect(str(TEST_DB_PATH))
        conn.execute(f"PRAGMA key = '{key}'")
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM clients;")
        row_count = cursor.fetchone()[0]
        conn.close()

        self.assertGreater(row_count, 0, "O banco deve retornar os registros cadastrados usando a chave correta.")

    @unittest.skipUnless(HAS_SQLCIPHER, "SQLCipher não disponível neste ambiente")
    def test_3_chave_incorreta(self):
        """Teste 3: Tentativa de abrir o banco com chave incorreta deve falhar."""
        close_connection()

        with self.assertRaises(Exception):
            conn = sqlcipher3_dbapi.connect(str(TEST_DB_PATH))
            conn.execute("PRAGMA key = 'CHAVE_TOTALMENTE_ERRADA_123'")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients;")
            cursor.fetchall()
            conn.close()

    def test_4_crud(self):
        """Teste 4: Verifica operações de CREATE, READ, UPDATE e DELETE via Repository/Service."""
        # 1. CREATE
        new_client_data = {
            "nome": "Empresa Teste CRUD Ltda",
            "cpf_cnpj": "11.222.333/0001-99",
            "cidade": "São Paulo",
            "uf": "SP"
        }
        created = ClientService.save_client(new_client_data)
        self.assertIsNotNone(created.get("id"), "Cliente criado deve receber um ID válido.")
        client_id = created["id"]

        # 2. READ
        found = ClientService.get_client_by_id(client_id)
        self.assertIsNotNone(found, "Cliente criado deve ser retornado pelo READ.")
        self.assertEqual(found["nome"], "Empresa Teste CRUD Ltda")

        # 3. UPDATE
        updated_data = {"id": client_id, "nome": "Empresa Teste CRUD Atualizada"}
        updated = ClientService.save_client(updated_data)
        self.assertEqual(updated["nome"], "Empresa Teste CRUD Atualizada")

        # 4. DELETE
        deleted_ok = ClientService.delete_client(client_id)
        self.assertTrue(deleted_ok, "Remoção do cliente deve retornar True.")
        self.assertIsNone(ClientService.get_client_by_id(client_id), "Cliente excluído não deve mais existir no banco.")

    def test_5_persistencia(self):
        """Teste 5: Inserir dados, fechar a conexão, reabrir e verificar se continuam salvos."""
        # Criar registro
        client_data = {
            "nome": "Cliente Persistente S/A",
            "cpf_cnpj": "99.888.777/0001-11",
            "cidade": "Campinas",
            "uf": "SP"
        }
        created = ClientService.save_client(client_data)
        client_id = created["id"]

        # Fechar completamente a conexão com o banco
        close_connection()

        # Re-inicializar a conexão com a chave correta
        init_engine(db_path=TEST_DB_PATH)

        # Verificar se o registro continua no banco
        persisted = ClientService.get_client_by_id(client_id)
        self.assertIsNotNone(persisted, "O registro deve persistir após reabrir a conexão.")
        self.assertEqual(persisted["nome"], "Cliente Persistente S/A")

if __name__ == "__main__":
    unittest.main()

"""
Suíte de Testes Automatizados do Módulo CRUD de Mecânicos (tests/test_mechanic_service.py).
"""
import os
import unittest
from pathlib import Path

from app.database.connection import init_engine, close_connection
from app.database.migrations import run_migrations
from app.services.mechanic_service import MechanicService

TEST_DB_PATH = Path(__file__).resolve().parent / "test_mechanics_app.db"

class TestMechanicService(unittest.TestCase):

    def setUp(self):
        close_connection()
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)

        init_engine(db_path=TEST_DB_PATH)
        run_migrations()

    def tearDown(self):
        close_connection()
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)

    def test_seeder_mechanics(self):
        """Verifica se os mecânicos padrão foram semeados no banco."""
        mechanics = MechanicService.get_all_mechanics()
        self.assertGreaterEqual(len(mechanics), 4, "Devem existir pelo menos 4 mecânicos semeados.")
        nomes = [m["nome"] for m in mechanics]
        self.assertIn("Carlos Eduardo", nomes)

    def test_crud_mechanic(self):
        """Verifica operações de CREATE, READ, UPDATE e DELETE de mecânicos."""
        # 1. CREATE
        new_data = {
            "nome": "Fernando Souza",
            "especialidade": "Mecânico Geral",
            "celular": "(11) 99999-1111",
            "cpf": "123.456.789-00",
            "ativo": True
        }
        created = MechanicService.save_mechanic(new_data)
        self.assertIsNotNone(created.get("id"))
        self.assertEqual(created["nome"], "Fernando Souza")
        m_id = created["id"]

        # 2. READ
        found = MechanicService.get_mechanic_by_id(m_id)
        self.assertIsNotNone(found)
        self.assertEqual(found["especialidade"], "Mecânico Geral")

        # 3. UPDATE
        update_data = {"id": m_id, "especialidade": "Especialista em Suspensão"}
        updated = MechanicService.save_mechanic(update_data)
        self.assertEqual(updated["especialidade"], "Especialista em Suspensão")

        # 4. FILTER
        filtered = MechanicService.filter_mechanics(nome_filter="Fernando")
        self.assertEqual(len(filtered), 1)

        # 5. DELETE
        deleted = MechanicService.delete_mechanic(m_id)
        self.assertTrue(deleted)
        self.assertIsNone(MechanicService.get_mechanic_by_id(m_id))

if __name__ == "__main__":
    unittest.main()

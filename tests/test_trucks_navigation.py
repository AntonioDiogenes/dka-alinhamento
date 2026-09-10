import unittest
import tkinter as tk
from unittest.mock import MagicMock
from app.views.trucks.finalizar import TrucksFinalizarView
from app.views.trucks.medidas import TrucksMedidasView

class TestTrucksNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from app.database.connection import init_engine
            from app.database.migrations import run_migrations
            init_engine()
            run_migrations()
        except Exception:
            pass
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except Exception:
            cls.root = None

    @classmethod
    def tearDownClass(cls):
        if cls.root:
            cls.root.destroy()

    def setUp(self):
        if not self.root:
            self.skipTest("Tkinter display not available")

    def test_finalizar_view_with_none_units_data(self):
        """Verifica se TrucksFinalizarView lida corretamente com kwargs com units_data=None"""
        mock_router = MagicMock()
        view = TrucksFinalizarView(self.root, mock_router, kwargs={"units_data": None})
        self.assertIsNotNone(view.composition_units)
        self.assertIsInstance(view.composition_units, list)
        self.assertGreater(len(view.composition_units), 0)
        view.destroy()

    def test_finalizar_view_with_composition_units(self):
        """Verifica se TrucksFinalizarView aceita composition_units"""
        mock_router = MagicMock()
        custom_units = [{"id": 1, "type": "Cavalo Mecânico", "model": "TEST TRUCK"}]
        view = TrucksFinalizarView(self.root, mock_router, kwargs={"composition_units": custom_units})
        self.assertEqual(view.composition_units, custom_units)
        view.destroy()

    def test_medidas_advance_next(self):
        """Verifica a transição de medidas para finalizar sem causar TypeError"""
        mock_router = MagicMock()
        view = TrucksMedidasView(self.root, mock_router, kwargs={"composition_units": [{"type": "Cavalo Mecânico", "front_axles": 1, "rear_axles": 1}]})
        view._on_advance_next()
        mock_router.navigate.assert_called_once()
        args, kwargs = mock_router.navigate.call_args
        self.assertEqual(args[0], "trucks.finalizar")
        self.assertIsNotNone(kwargs.get("units_data"))
        self.assertIsNotNone(kwargs.get("composition_units"))
        view.destroy()

    def test_control_panel_layout(self):
        """Verifica se o ControlPanel tem os botões de navegação instanciados e scroll_canvas"""
        from app.components.control_panel import ControlPanel
        mock_advance = MagicMock()
        mock_modal = MagicMock()
        panel = ControlPanel(
            self.root,
            active_axle_name="Dianteiro 1",
            on_advance=mock_advance,
            on_open_axle_modal=mock_modal
        )
        self.assertIsNotNone(panel.btn_switch_axle)
        self.assertIsNotNone(panel.scroll_canvas)
        self.assertIn("Dianteiro 1", panel.btn_switch_axle.cget("text"))
        
        panel.update_active_axle("Traseiro 1")
        self.assertIn("Traseiro 1", panel.btn_switch_axle.cget("text"))
        panel.destroy()

    def test_client_form_masks(self):
        """Verifica a aplicação automática da máscara de Telefone Fixo no ClientForm"""
        from app.components.client_form import ClientForm
        form = ClientForm(self.root, client_data={"telefone_fixo": "1133445566"})
        self.assertEqual(form.var_telefone.get(), "(11) 3344-5566")

        form.var_telefone.set("1332119988")
        self.assertEqual(form.var_telefone.get(), "(13) 3211-9988")
        form.destroy()

if __name__ == "__main__":
    unittest.main()


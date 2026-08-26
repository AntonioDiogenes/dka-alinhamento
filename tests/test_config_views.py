import unittest
from app.services.truck_service import TruckService

class TestConfigViews(unittest.TestCase):
    def test_brands_and_models_management(self):
        # 1. Testar busca de marcas
        brands = TruckService.get_brands_summary()
        self.assertIsInstance(brands, list)
        self.assertGreater(len(brands), 0)
        self.assertIn("brand_name", brands[0])
        self.assertIn("brand_code", brands[0])

        # 2. Testar busca de modelos
        trucks = TruckService.get_all_trucks()
        self.assertIsInstance(trucks, list)
        self.assertGreater(len(trucks), 0)
        model = trucks[0]

        # 3. Testar edição de modelo
        model_id = model["id"]
        orig_name = model["model_name"]
        new_name = orig_name + " (EDITADO TESTE)"

        success = TruckService.update_model(model_id, {"model_name": new_name})
        self.assertTrue(success)

        # Re-testar restauração do nome original
        TruckService.update_model(model_id, {"model_name": orig_name})

if __name__ == "__main__":
    unittest.main()

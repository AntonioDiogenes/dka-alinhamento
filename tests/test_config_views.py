"""
Teste unitário para a camada de serviço e repositório de Marcas e Modelos.
"""
from app.services.truck_service import TruckService

def test_brands_and_models_management():
    # 1. Testar busca de marcas
    brands = TruckService.get_brands_summary()
    assert isinstance(brands, list)
    assert len(brands) > 0
    assert "brand_name" in brands[0]
    assert "brand_code" in brands[0]

    # 2. Testar busca de modelos
    trucks = TruckService.get_all_trucks()
    assert isinstance(trucks, list)
    assert len(trucks) > 0
    model = trucks[0]

    # 3. Testar edição de modelo
    model_id = model["id"]
    orig_name = model["model_name"]
    new_name = orig_name + " (EDITADO TESTE)"

    success = TruckService.update_model(model_id, {"model_name": new_name})
    assert success is True

    # Re-testar restauração do nome original
    TruckService.update_model(model_id, {"model_name": orig_name})

    print("✅ Testes de gerenciamento de Marcas e Modelos concluídos com sucesso!")

if __name__ == "__main__":
    test_brands_and_models_management()

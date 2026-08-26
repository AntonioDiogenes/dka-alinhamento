"""
Serviço de Catálogo e Seleção de Caminhões (services/truck_service.py).
Conecta as Views de Truck com o TruckRepository e a camada de banco criptografado SQLCipher.
"""
from typing import List, Dict, Any
from app.database.repositories.truck_repository import TruckRepository

class TruckService:
    @staticmethod
    def get_all_trucks() -> List[Dict[str, Any]]:
        return TruckRepository.get_all()

    @staticmethod
    def get_manufacturers() -> List[str]:
        return TruckRepository.get_manufacturers()

    @staticmethod
    def filter_trucks(
        search_text: str = "",
        manufacturer: str = "Todos os fabricantes",
        search_query: str = "",
        brand_filter: str = "Todos os fabricantes",
        **kwargs
    ) -> List[Dict[str, Any]]:
        return TruckRepository.filter(
            search_text=search_text,
            manufacturer=manufacturer,
            search_query=search_query,
            brand_filter=brand_filter,
            **kwargs
        )

    @staticmethod
    def get_brands_summary() -> List[Dict[str, Any]]:
        return TruckRepository.get_brands_summary()

    @staticmethod
    def update_brand(old_brand_name: str, new_brand_name: str, new_brand_code: str) -> bool:
        return TruckRepository.update_brand(old_brand_name, new_brand_name, new_brand_code)

    @staticmethod
    def update_model(model_id: int, data: Dict[str, Any]) -> bool:
        return TruckRepository.update_model(model_id, data)
